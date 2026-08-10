import os


# 개발 환경에서는 기본값을 사용하고, 배포 환경에서는 환경 변수로 교체한다.
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "development-only-secret-key")
