# Use the official Python image as base
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy project
COPY . /app/
# Install dependencies
COPY requirement.txt /app/

RUN pip install -r requirement.txt


# Run migrations and collect static files
RUN #python manage.py collectstatic
RUN python manage.py check


COPY env.example ./.env
# Expose port 8000
EXPOSE 8000

RUN #python manage.py runserver

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]