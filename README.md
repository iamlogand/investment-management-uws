# Investment Management App

This is the codebase for my Hons Project web application. The app is deployed to Heroku at [https://investment-management-uws.herokuapp.com](https://investment-management-uws.herokuapp.com).

## Features

The app is a work in progress, but current features include:

- User authentication, including email validation
- Create portfolios
- Register Investment Accounts (currently limited to FreeTrade and Trading 212)
- Register cash deposit and withdrawal events
- Register security purchase and sale events
- View latest prices for securities, updated every 10 minutes

## Limitations

The app takes about 15 seconds to load after at least 30 minutes of inactivity. This is a consequence of using Heroku's free package.

This app depends on a free, but limited, email server. Consequently, verification and password reset emails can only be sent to already whitelisted email addresses.

If you require your email to be whitelisted, don't hesitate to contact me at [b00289028@studentmail.uws.ac.uk](mailto:b00289028@studentmail.uws.ac.uk).