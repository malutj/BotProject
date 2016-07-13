import os

server = os.environ['SERVER']


botAlphaPageKey = ( 'EAARBuHDd8IYBAPVnZBaXX6kXbvwhHAADuMLXgZA5CXLMkNPvK5s0KzkzBl'
                 'jfFfUTut5K5DQeTKZBdEEY5bltZA601o5IrxUbMYL1xlBaLw9toCf329TPN'
                 'zcX9bdi6bpfowtQzeiYx5pXqm6amtHzfYNHGZAJR3IAGJPXZAfka7ZCQZDZD' )

botAlphaPageToken = 'malutj'

botTestPageKey  = ( 'EAAY8WTjoQGkBAEQDhKm0dSO1ZAsKIZApTGZAJaxsZCoRO41ATCyrNMbsLQu'
                 'yMNNRXNJg34HZAkZCdtCRbSIXVdF6fdzqQazKCGuf3wrn0LUhW8wTIXTaMee'
                 'QNfQrltaeIXjirZAZC0ydZBH7ZADZAo37u7Ec2TUC2M3tbl5cvP5f1rZApwZDZD' )

botTestPageToken = 'malutj'

releaseToken = 'a64f65974d0a43ab1302'


applicationKey = 0

if (server == 'HEROKU'):
    applicationKey = botAlphaPageKey
else:
    applicationKey = botTestPageKey
