from typing import Literal

from pydantic import BaseModel


class ReportAnalyticsEventCreate(BaseModel):
    event_name: Literal["report_viewed", "report_copied"]
