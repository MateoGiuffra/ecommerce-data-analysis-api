from src.services.metrics.metrics_service import MetricsService
from src.services.cache_service import CacheService
from pandas import DataFrame
from src.schemas.metrics import *
from typing import List
from src.repositories.metrics_repository import MetricsRepository
from src.schemas.pagination import PageParams, PageResponse
import pandas as pd
from math import ceil

class CustomerService(MetricsService):
    def __init__(self, metrics_repository: MetricsRepository, cache_service: CacheService, cache_df_ttl_seconds: int):
        super().__init__(metrics_repository, cache_service, cache_df_ttl_seconds)
        
    async def get_top_spenders(self, top_spenders_params: TopSpendersMetricsParams) -> List[Spender]:
        db: DataFrame = await self.get_clean_data_frame()
        top_spenders = (
            db.groupby(self.customer_id)
            .agg(
                total_spent=(self.total_price, "sum"),
                total_units_sold=(self.quantity, "sum"),
                total_sells=(self.invoice_no, "nunique")
                )
            .sort_values(by="total_spent", ascending=top_spenders_params.ascending)
            .head(top_spenders_params.limit)
        )
        
        return [
            Spender(customer_id=str(customer_id), **row.to_dict())
            for customer_id, row in top_spenders.iterrows()
        ]
        
    def get_score_list_asc(self, max_score: int) -> List[int]:
        return [i for i in range(max_score, 0, -1)]

    def get_score_list_desc(self, max_score: int) -> List[int]:
        return [i for i in range(1, max_score + 1)]


    def get_segment_name(self, r_score: int, f_score: int, m_score: int, max_score: int) -> SegmentName:        
        # 1. CHAMPIONS (R=5, F=5, M=5) - Top priority
        if r_score == max_score and f_score == max_score and m_score == max_score:
            return SegmentName.CHAMPIONS
        
        # 2. LOYALTIES (High R, Mid/High F/M)
        # They purchased recently and have good value/frequency (e.g., 4, 3, 3)
        if r_score >= 4 and f_score >= 3 and m_score >= 3:
            return SegmentName.LOYALTIES

        # 3. ALMOST_LOST (Low R, High F/M) - URGENT
        # Very low recency, but they have a history of good spend/frequency (e.g., 1, 5, 5).
        # This segment is the most critical to reactivate.
        if r_score <= 2 and f_score >= 4 and m_score >= 4:
            return SegmentName.ALMOST_LOST
        
        # 4. EN_RISK / NEED_ATTENTION (Mid/Low R, Mid F/M)
        # They have started to decline.
        if r_score <= 3 and f_score >= 3 and m_score >= 3:
            # If recency is medium (3) or low (1-2), and value is good:
            if r_score >= 3: # Recency of 3
                return SegmentName.NEED_ATTENTION
            else: # Recency of 1 or 2
                return SegmentName.EN_RISK

        # 5. RECENTS (High R, Low F/M)
        # They purchased recently but don't have much history yet.
        if r_score >= 4 and f_score <= 2:
            return SegmentName.RECENTS

        # 6. SLEEPER (Low R, Low F/M) - Low value
        # Very low-value, low-activity customers.
        if r_score <= 2 and f_score <= 2 and m_score <= 2:
            return SegmentName.SLEEPER
        
        return SegmentName.NEED_ATTENTION

    def _safe_qcut(self, series: pd.Series, q: int, labels: List[int]):
        """Attempt to cut `series` into `q` quantiles with `labels`.
        Falls back to a stable procedure when qcut raises ValueError due to
        non-unique bin edges (e.g., many identical values).
        Returns a pandas Series of labels (same index as input).
        """
        try:
            return pd.qcut(series, q=q, labels=labels)
        except ValueError:
            # If there are too few unique values, qcut may fail.
            uniq = series.nunique()
            if uniq <= 1:
                # All values identical or empty: assign the middle label
                mid_label = labels[len(labels) // 2]
                return pd.Series([mid_label] * len(series), index=series.index)

            # Use qcut with duplicates dropped to get categories, then map codes to a subset of labels
            cat = pd.qcut(series, q=q, duplicates="drop")
            bins = cat.cat.categories.size
            labels_for_bins = labels[:bins]
            codes = cat.cat.codes
            mapped = [labels_for_bins[c] if c >= 0 else None for c in codes]
            return pd.Series(mapped, index=series.index)


    async def get_rfm_analysis_page(self, page_params: PageParams) -> PageResponse[RFMAnalysis]: 
        all_results: List[RFMAnalysis] = await self.get_rfm_analysis()
        all_results = sorted(all_results, key=lambda r: (r.get("total_spend", 0), r.get("frequency", 0)), reverse=True)
        
        total_results = len(all_results)
        limit = max(1, int(page_params.limit))
        page = max(1, int(page_params.page))

        total_pages = ceil(total_results / limit) if total_results > 0 else 1

        start = (page - 1) * limit
        end = start + limit
        page_slice = all_results[start:end]

        return PageResponse(
            results=page_slice,
            page=page,
            limit=limit,
            total_pages=total_pages,
            total_results=total_results,
        )
        
    async def get_rfm_analysis(self, max_score: int = 5) -> List[RFMAnalysis]:
        """
        RFM (Recency, Frequency, Monetary) Analysis
        Returns segments clients (Champions, Loyalties, In risk)
        """
        df: DataFrame = await self.get_clean_data_frame()

        snapshot_date = pd.to_datetime(df[self.invoice_date]).max() + pd.Timedelta(days=1)
        df_rfm = (
            df.groupby(self.customer_id)
            .agg(
        recency=(self.invoice_date, lambda x: int((snapshot_date - pd.to_datetime(x.max())) / pd.Timedelta(days=1))),
                frequency=(self.invoice_no, "nunique"),
                monetary=(self.total_price, "sum"),
                )
        )
        
        df_rfm["r_score"] = self._safe_qcut(
            df_rfm['recency'],
            q=max_score,
            labels=self.get_score_list_asc(max_score)
        )
        
        df_rfm["f_score"] = self._safe_qcut(
            df_rfm['frequency'],
            q=max_score,
            labels=self.get_score_list_desc(max_score)
        )
        
        df_rfm["m_score"] = self._safe_qcut(
            df_rfm['monetary'],
            q=max_score,
            labels=self.get_score_list_desc(max_score)
        )
        rfm_analysis_list: List[RFMAnalysis] = []
        
        for _, row in df_rfm.iterrows():
            try:
                recency_score = int(row["r_score"])
            except Exception:
                recency_score = 0

            try:
                frequency_score = int(row["f_score"])
            except Exception:
                frequency_score = 0

            try:
                monetary_score = int(row["m_score"])
            except Exception:
                monetary_score = 0

            # Call get_segment_name with the parameter names the method expects
            segment_name: SegmentName = self.get_segment_name(r_score=recency_score, f_score=frequency_score, m_score=monetary_score, max_score=max_score)
            
            rfm_analysis_list.append(
                RFMAnalysis(
                    recency=recency_score,
                    frequency=frequency_score,
                    monetary=monetary_score,
                    segment_name=segment_name,
                    total_spend=row["monetary"]
                )
            )
            
        return rfm_analysis_list
            
            

            
            
            
        
