FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create entrypoint
RUN echo '#!/bin/bash\npython manage.py migrate\nexec python manage.py runserver 0.0.0.0:8000' > entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]