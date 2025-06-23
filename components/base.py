"""
Base component classes with proper abstraction
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ComponentProps:
    """Base props for all components"""
    className: Optional[str] = None
    id: Optional[str] = None
    style: Optional[Dict[str, Any]] = None


class BaseComponent(ABC):
    """Base component class"""

    def __init__(self, props: ComponentProps) -> None:
        self.props = props

    @abstractmethod
    def render(self) -> Any:
        """Render the component"""
        pass

    def validate_props(self) -> List[str]:
        """Validate component props"""
        return []


class ChartComponent(BaseComponent):
    """Base class for chart components"""

    def __init__(self, props: ComponentProps, data: Dict[str, Any]) -> None:
        super().__init__(props)
        self.data = data

    def validate_props(self) -> List[str]:
        errors: List[str] = []
        if not self.data:
            errors.append("Chart data cannot be empty")
        return errors
