from enum import StrEnum

from typing import Union


class EventLogLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def get_severity_map(cls) -> dict[str, int]:
        return {
            cls.INFO: 1, 
            cls.WARNING: 2,
            cls.ERROR: 3, 
            cls.CRITICAL: 4
        }
    
    def compare(self, other: Union['EventLogLevel', str]) -> tuple[int, int]:
        '''returns the int repr of the log levels
        Arguments:
            other {Union[&#39;EventLogLevel&#39;, str]} -- _description_

        Returns:
            tuple[int, int] -- self, other
        '''
        if isinstance(other, str):
            other = EventLogLevel(other)

        hierarchy = EventLogLevel.get_severity_map()
        return hierarchy.get(self, -1), hierarchy.get(other, -1)

    def __lt__(self, other: Union['EventLogLevel', str]) -> bool:
        self_severity, other_severity = self.compare(other)
        return self_severity < other_severity

    
    def __gt__(self, other: Union['EventLogLevel', str]) -> bool:
        self_sererity, other_severity = self.compare(other)
        return self_sererity > other_severity
                
    def __ge__(self, other: Union['EventLogLevel', str]) -> bool:
        self_severity, other_severity = self.compare(other)
        return self_severity >= other_severity