FROM selenium/standalone-chrome

USER root

WORKDIR /tests

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "test_ecommerce.py", "-v", "--tb=short", "--junit-xml=test-results.xml"]
