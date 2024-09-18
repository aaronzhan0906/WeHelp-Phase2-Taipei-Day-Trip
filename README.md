## Taipei Day Trip

Website URL : https://taipeidaytrip.online/

Taipei Day Trip is a website that lets users discover and explore unique attractions in Taipei. Visitors can book and pay for their chosen trips!

```code
Test Account: test@gmail.com
Test Password: test
```


```code
Test card number: 4242 4242 4242 4242
Expiration Date: 12/34
CCV: 123
```
![TDT 1](https://github.com/user-attachments/assets/55650a2b-6bea-42f7-9b3c-33ffcc9d329d)



#### Features and Techniques

- Member system : **JWT token-based** authentication
- Online shopping : Shopping cart system, Infinite scroll, lazy loading, and Carousel Slider
- Cross-device compatibility: **Responsive Web Design** (**RWD**) using vanilla **JavaScript**, **CSS**, and **HTML**
- Online payments: Integration of **TapPay SDK** third-party payment service
- Data management: Normalized **MySQL** database in **3NF** with optimized queries using indexes and connection pooling
- Cache: **Redis** caching for recently used image links
- Frontend-backend communication: **RESTful API** implementation
- Web server: **Nginx** for reverse proxy and **SSL** services
- Cloud deployment: **AWS EC2** instances managed with **Docker-Compose**

## Architecture
<img width="854" alt="TDT-Architecture" src="https://github.com/user-attachments/assets/0e1d09d5-8df3-4a4b-8141-7c130041b91f">

## Backend Technique
#### Language / Framework
- Python / FastAPI
#### Database
- MySQL
- Redis
#### Cloud Service (AWS)
- EC2
- Route 53

#### Containerize
- Docker
- Docker-compose

#### Authentication and Authorization 
- JWT

#### Infrastructure
- Nginx
- SSL(CertBot)

#### Third Party Libraries
- aiohttp: Asynchronous HTTP client/server framework
- bcrypt: Password hashing
- mysql-connector-python: MySQL database driver
- pydantic: Data validation and settings management
- python-dotenv: Loads environment variables from .env files
- PyJWT: JSON Web Token implementation
- shortuuid: Generation of order numbers
- TapPay SDK: Payment processing integration
- uvicorn: ASGI server

#### Payment Integration
- TapPay SDK: Payment processing integration

## Database Schema
<img width="1074" alt="TDT-database schema" src="https://github.com/user-attachments/assets/67d1d9a8-b3b4-4082-94e0-51fce1becdd9">