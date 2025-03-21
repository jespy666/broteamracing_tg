from .booking.handlers import booking_router
from .simple.handlers import simple_router
from .admin.handlers import admin_router
from .staff.handlers import staff_router


__all__ = ("booking_router", "simple_router", "admin_router", "staff_router")
