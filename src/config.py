from datetime import timedelta

LOCK_ID = 3215
CHECKIN_NOTICE = timedelta(hours=24)  # Notify 24 hours before arrival
SMS_NOTICE = timedelta(hours=24)      # Send SMS 24 hours before arrival
BUFFER_BEFORE = timedelta(hours=0)    # No buffer before check-in (overlap allowed)
BUFFER_AFTER = timedelta(hours=0)     # No buffer after check-out (overlap allowed)