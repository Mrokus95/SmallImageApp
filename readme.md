# SmallImage App
[![AWS RDS](https://img.shields.io/badge/AWS%20RDS-Cloud-orange)](https://aws.amazon.com/rds/) 
[![AWS S3](https://img.shields.io/badge/AWS%20S3-Cloud-orange)](https://aws.amazon.com/s3/) 
[![AWS CloudFront](https://img.shields.io/badge/AWS%20CloudFront-Cloud-orange)](https://aws.amazon.com/cloudfront/) 
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-yellow)](https://www.postgresql.org/) 
[![Django DRF](https://img.shields.io/badge/Django%20DRF-Backend-blue)](https://www.django-rest-framework.org/) 
[![Python](https://img.shields.io/badge/Python-Backend-blue)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-Testing-green)](https://docs.pytest.org/en/7.4.x/) 
[![Docker-compose](https://img.shields.io/badge/Docker%20compose-Other-purple)](https://docs.docker.com/)
[![Django-rest-knox](https://img.shields.io/badge/Django%20rest%20knox-Other-purple)](https://github.com/jazzband/django-rest-knox)

Welcome to the SmallImage App!

This is a Django Rest Framework (DRF) project that enables users to upload images and acquire links to their thumbnails. If you don't have much time to install the project but are interested in it, you can check out the live version of SmallImage <a href="https://imageapp-ereajzel.pythonanywhere.com/"> HERE</a> with this test account: 
- username : TestUser , 
- password : TestPassword
TestUser's password resets every hour, so feel free to test the password change endpoint as well. Just keep in mind that this project has throttling limits, so if you need more request vouchers (error HTTP 429 (Too Many Requests)), please contact me or wait until the next day for a refresh."


## Table of contents
* [Manual Installation Process](#manual-installation-process)
* [Installation process with docker](#installation-process-with-docker)
* [How it works](#how-it-works)
* [Key features](#key-features)
* [API documentation](#api-documentation)
* [Tests and validation](#tests-and-validation)
* [Future plans](#future-plans)

## Manual Installation Process:

1. Clone the repository to your local computer:

    ```
    $ git clone 'https://github.com/Mrokus95/SmallImageApp.git'
    ```

2. Navigate to the project directory:

    ```
    $ cd imageapp
    ```

3. (Optional) It is recommended to create and activate a Python virtual environment:

    ```
    $ python -m venv venv
    $ python venv/bin/activate
    ```

4. Install the required dependencies:

    ```
    $ pip install -r requirements.txt
    ```

5. Create file .env in and set the environment variables:

    **General Django settings:**
    - `SECRET_KEY`: Django secret key (automatically generated when creating a Django project)

    **AWS RDS settings:**
    - `POSTGRES_NAME`: The database name.
    - `POSTGRES_USER`: The username that you configured for your database.
    - `POSTGRES_PASSWORD`: The password that you configured for your database.
    - `POSTGRES_HOST`: The hostname of the DB instance.
    - `POSTGRES_PORT`: The port where the DB instance accepts connections. The default value varies among DB engines.

    **AWS S3 settings:**
    - `AWS_ACCESS_KEY_ID`: Your AWS S3 Access Key ID. This is required for authenticating access to S3.
    - `AWS_SECRET_ACCESS_KEY`: Your AWS S3 Secret Access Key, which is used in conjunction with the Access Key ID for authenticating access to S3.
    - `AWS_STORAGE_BUCKET_NAME`: The name of the bucket in AWS S3 where your files will be stored.
    - `AWS_S3_REGION_NAME`: The AWS region in which your S3 bucket is located. For example, "us-east-1" for the US East (N. Virginia) region.
    - `AWS_S3_SIGNATURE_VERSION`: The version of the signature used for authenticating access to S3.
    - `AWS_S3_ADDRESSING_STYLE`: The addressing style used for constructing S3 URL addresses.
    - `AWS_S3_ENDPOINT_URL`: Optional S3 endpoint URL that allows customization of where your S3 requests are directed.

    **AWS CloudFront settings:**
    - `AWS_QUERYSTRING_AUTH`: A flag to indicate whether to use query strings for authentication with CloudFront. If set to True, it enables query string authentication. If set to False, query strings are not used for authentication.
    - `AWS_S3_CUSTOM_DOMAIN`: An optional custom domain name that you can use with CloudFront. If specified, it allows you to use a custom domain for your content distribution.
    - `AWS_CLOUDFRONT_KEY_ID`: The key ID associated with your AWS CloudFront key. This is used for authentication and access control with CloudFront.
    - `AWS_CLOUDFRONT_KEY`: The CloudFront key used for secure access to your content. RSA Private key.

    **Django superuser settings:**
    - `DJANGO_SUPERUSER_USERNAME`: The superuser username.
    - `DJANGO_SUPERUSER_PASSWORD`: The superuser password.
    - `DJANGO_SUPERUSER_EMAIL`: The superuser email.

    You can set the environment variables on your operating system or place them in a .env file in the project's root directory.


6. Run the Django development server:

    ```
    $ python manage.py runserver
    ```

    The application will be available at http://localhost:8000/.

## Installation process with docker:

1. Clone the repository to your local computer:

    ```
    $ git clone 'https://github.com/Mrokus95/SmallImageApp.git'
    ```

4. Create file .env and set the environment variables:

    **General Django settings:**
    - `SECRET_KEY`: Django secret key (automatically generated when creating a Django project)

    **AWS RDS settings:**
    - `POSTGRES_NAME`: The database name.
    - `POSTGRES_USER`: The username that you configured for your database.
    - `POSTGRES_PASSWORD`: The password that you configured for your database.
    - `POSTGRES_HOST`: The hostname of the DB instance.
    - `POSTGRES_PORT`: The port where the DB instance accepts connections. The default value varies among DB engines.

    **AWS S3 settings:**
    - `AWS_ACCESS_KEY_ID`: Your AWS S3 Access Key ID. This is required for authenticating access to S3.
    - `AWS_SECRET_ACCESS_KEY`: Your AWS S3 Secret Access Key, which is used in conjunction with the Access Key ID for authenticating access to S3.
    - `AWS_STORAGE_BUCKET_NAME`: The name of the bucket in AWS S3 where your files will be stored.
    - `AWS_S3_REGION_NAME`: The AWS region in which your S3 bucket is located. For example, "us-east-1" for the US East (N. Virginia) region.
    - `AWS_S3_SIGNATURE_VERSION`: The version of the signature used for authenticating access to S3.
    - `AWS_S3_ADDRESSING_STYLE`: The addressing style used for constructing S3 URL addresses.
    - `AWS_S3_ENDPOINT_URL`: Optional S3 endpoint URL that allows customization of where your S3 requests are directed.

    **AWS CloudFront settings:**
    - `AWS_QUERYSTRING_AUTH`: A flag to indicate whether to use query strings for authentication with CloudFront. If set to True, it enables query string authentication. If set to False, query strings are not used for authentication.
    - `AWS_S3_CUSTOM_DOMAIN`: An optional custom domain name that you can use with CloudFront. If specified, it allows you to use a custom domain for your content distribution.
    - `AWS_CLOUDFRONT_KEY_ID`: The key ID associated with your AWS CloudFront key. This is used for authentication and access control with CloudFront.
    - `AWS_CLOUDFRONT_KEY`: The CloudFront key used for secure access to your content. RSA Private key.

    **Django superuser settings:**
    - `DJANGO_SUPERUSER_USERNAME`: The superuser username.
    - `DJANGO_SUPERUSER_PASSWORD`: The superuser password.
    - `DJANGO_SUPERUSER_EMAIL`: The superuser email.

    You can set the environment variables on your operating system or place them in a .env file in the project's root directory.

5. Build an image:

    ```
    $ docker-compose build
    ```

6. Run the container:

    ```
    $ docker-compose run -d
    ```

The application will be accessible at http://localhost:8000/, which is the API documentation page. The superuser, along with three basic account types and migrations, are already set up for you and yours new users. Enjoy `:)`.

## How it works
This application empowers users to effortlessly upload graphic files in popular formats such as .png, .jpg, and .jpeg to the application's server. It provides a platform that caters to a diverse user base, enabling them to manage and access their image assets in an efficient and secure manner.

First step? Use your superuser's login and password at login endpoint. In response you will obtain a token which will be used to authenticate you at other endpoints. Next, try to send an image to SmallImage App using POST method with /users/images/ endpoint. 
Next, its time for GET method to revele your links to thumbanils and original image - choose the best and save its id and type (image or thumbnail). At the and generate and share with friend a time-limited link to your new thumbnail with /users/generate-temp-link/<file_type>/<file_id>/ endpoint.


## Key features:

1.  Flexible Account Types:

    - Basic Account Typeid => 1:
        - Original image link: No
        - Time-limited link: No
        - Thumbanil sizes : 200 px

    - Premium Account Type id => 2:
        - Original image link: Yes
        - Time-limited link: No
        - Thumbanil sizes : 200 px, 400 px

    - Enterprise Account Type id => 3:
        - Original image link: Yes
        - Time-limited link: Yes
        - Thumbanil sizes : 200 px, 400 px

    Users can choose from these account types, each offering distinct advantages based on their specific needs.

2.  Image and Thumbnail Access:
    Depending on the chosen account type, users gain access to either the original images or predefined thumbnails. This tailored access ensures efficient resource utilization and a seamless experience.

3.  Temporary Link Generation:
    Enterprise account users can generate temporary links to access specific images or thumbnails for a predefined duration. This feature is a valuable asset for time-sensitive use cases.

4.  Token-Based Authentication:
    The application enforces robust token-based authentication, ensuring that user data and assets remain secure.

5.  Efficient AWS Integration:
    To enhance performance and reliability, the application leverages Amazon Web Services (AWS). AWS RDS provides a scalable and efficient database solution, while AWS S3 hosts static files, streamlining asset management.

6.  Reduced Latency with CloudFront:
    The use of AWS CloudFront significantly reduces latency, ensuring that images load swiftly and users experience minimal delays.

7.  Presigned URLs for Secure Access:
    Secure image and thumbnail access is facilitated through the implementation of presigned URLs. Users can confidently share and access resources while adhering to defined access periods.

8.  Dynamic Thumbnail Generation:
    Miniature versions of images are dynamically created using the Pillow library, offering users a range of viewing options.

9.  Testing with Pytest:
    Rigorous testing is conducted using Pytest. The application can operate independently from AWS services during testing, using in-memory data and mocks for a seamless testing environment.

10. Containerized with Docker:
    The entire application is containerized using Docker, streamlining deployment and offering a consistent environment for development and production.

Project Benefits:

- Scalability: AWS-based infrastructure supports scalability, ensuring the application can grow with user demand.

- Speed and Reliability: Reduced latency through CloudFront and presigned URLs result in fast and reliable image access.

- Security: Token-based authentication and secure presigned URLs protect user data and assets.

- Flexibility: Users can choose account types that suit their specific image management requirements.

- Ease of Use: The application's user-friendly design and features simplify image and asset management.

- Efficiency: Dynamic thumbnail generation and efficient AWS integration enhance overall performance.

- Consistency: Docker containerization offers a consistent environment for development and deployment.

This application is designed to empower users and streamline image management, offering benefits that cater to a broad spectrum of users and use case

## API documentation:

The API documentation was created using drf-spectacular and Swagger. The API documentation page is the project's homepage at http://localhost:8000/.

### Endpoints map:
- Endpoint: /users/create/
    -   Description: Create a new user.
    -   Request Parameters:
        -   Authorization: Token should be included in the Authorization header as "Token your_token_here".
        -   username: User's username (required).
        -   email: User's email address (required).
        -   password: User's password, minimum length: 7 (required).
        -   account_type: User's account type ID (required).


-   Endpoint: /users/change-password/
    -   Description: Change a user's password.
    -   Request Parameters:
        -   Authorization: Token should be included in the Authorization header as "Token your_token_here".
        -   old_password: User's actual password (required).
        -   new_password: User's new password, minimum length: 7 (required).
        
-   Endpoint: /users/login/
    -   Description: User login.
    -   Request Parameters:
        -   username: User username (required).
        -   password: User password (required).

-   Endpoint: /users/logout/
    -   Description: User logout.
    -   Request Parameters:
        -   Authorization: Token should be included in the Authorization header as "Token your_token_here".

-   Endpoint: /users/logout-all/
    -   Description: User logout at all devices.
    -   Request Parameters:
        -   Authorization: Token should be included in the Authorization header as "Token your_token_here".

-   Endpoint: /users/manage/
    -   Description: Get user profile data.
    -   Request Parameters:
        -   Authorization: Token should be included in the Authorization header as "Token your_token_here".

-   Endpoint: /users/images/
    -   Description: Manage user images (list, retrieve, create, and delete).
    -   Request Parameters:
        -   Authorization: Token should be included in the Authorization header as "Token your_token_here".
        
-   Endpoint: /users/generate-temp-link/<file_type>/<file_id>/
    -   Description: Generate temporary links to access images or thumbnails.
    -   Request Parameters:
        -   Authorization: Token should be included in the Authorization header as "Token your_token_here".
        -   expiration_time_seconds: Expiration time in seconds, default 3600 (optional).


## Tests and validation

The project is covered by unit tests. I have made efforts to sensibly validate data, preventing the input of absurd data such as negative image sizes or adding images in formats other than required. At the same time, I have avoided excessive querying of the database when it is unnecessary.
Test are made using Pytest, factories and Faker. To speed up tests application set up additional datebase and save media files locally.

## Future plans

In the future, it would be worthwhile to consider the implementation of a queuing system 
like Celery to handle a large number of requests asynchronously.

Łukasz Mroczkowski
