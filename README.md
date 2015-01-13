#My Shipper API

API for getting rates and generating labels from USPS.

### GET rates/
| Query Parameter  | Notes  |
|---|---|
| o_zip |  _required_, Origin Zip Code |
| d_zip  | _required_, Destination Zip Code  |
| lbs  | _required_, Weight in pounds  |
| mail_class  |  _optional_, USPS Service type of: Priority,First Class,Standard Post,Media Mail, Library Mail |
| fcm_type | required if mail_class = First Class; of: LETTER, Flat, Parcel, Postcard, or Package Service |
|  oz | _optional_, Weight in ounces, if over 1 lb|
|  container | _optional_, useful for USPS container types, _default_=VARIABLE|
|  size | _optional_, used for USPS weight types, _default_=REGULAR, can be REGULAR or LARGE  |
| length  |  required if size is LARGE, in inches |
|  width |  required if size is LARGE in inches|
|  height | required if size is LARGE  in inches|
|  girth |  required if size is LARGE in inches|
|  machinable  | required if mail_class is First Class and fcm is Letter or Flat, either true or false|

####Sample GET Request with Required Parameters Only

```` 
/rates/?o_zip=78756&d_zip=78701&lbs=2
````
####Sample Response

````
{"data": [{"Rate": "19.15", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;"}, {"Rate": "19.15", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Hold For Pickup"}, {"Rate": "44.95", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Boxes"}, {"Rate": "44.95", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Boxes Hold For Pickup"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Envelope"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Envelope Hold For Pickup"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Legal Flat Rate Envelope"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Legal Flat Rate Envelope Hold For Pickup"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Padded Flat Rate Envelope"}, {"Rate": "19.99", "Mail Class": "Priority Mail Express 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Padded Flat Rate Envelope Hold For Pickup"}, {"Rate": "5.95", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;"}, {"Rate": "17.90", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Large Flat Rate Box"}, {"Rate": "12.65", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Medium Flat Rate Box"}, {"Rate": "5.95", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Small Flat Rate Box"}, {"Rate": "5.75", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Flat Rate Envelope"}, {"Rate": "5.90", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Legal Flat Rate Envelope"}, {"Rate": "6.10", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Padded Flat Rate Envelope"}, {"Rate": "5.75", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Gift Card Flat Rate Envelope"}, {"Rate": "5.75", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Small Flat Rate Envelope"}, {"Rate": "5.75", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt; Window Flat Rate Envelope"}, {"Rate": "3.17", "Mail Class": "Media Mail Parcel"}, {"Rate": "3.02", "Mail Class": "Library Mail Parcel"}]}
````
####Sample GET Request with Mail Class Specified

```` 
/rates/?o_zip=78756&d_zip=78701&lbs=2&mail_class=priority
````
####Sample Response

````
{"data": [{"Rate": "5.95", "Mail Class": "Priority Mail 1-Day&lt;sup&gt;&#8482;&lt;/sup&gt;"}]}
````

### GET label/

| Query Parameter  | Notes  |
|---|---|
| f_name |  _required_, Sender Name |
| f_company |  _optional_, Sender company name |
| f_address_1 |  _optional_, Sender Address Line 1, for apartment, suite number, etc.|
| f_address_2 |  _required_, Sender Address Line 2, street address |
| f_city |  _required_, Sender City |
| f_state |  _required_, Sender State Code, two characters eg. TX or WA |
| f_zip5 |  _required_, Sender Zip Code |
| f_zip4 |  _optional_, Sender +4 Zip Code |
| to_name |  _required_, Receiver Name |
| to_company |  _optional_, Receiver company name |
| to_address_1 |  _optional_, Receiver Address Line 1, for apartment, suite number, etc.|
| to_address_2 |  _required_, Receiver Address Line 2, street address |
| to_city |  _required_, Receiver City |
| to_state |  _required_, Receiver State Code, two characters eg. TX or WA |
| to_zip5 |  _required_, Receiver Zip Code |
| to_zip4 |  _optional_, Receiver +4 Zip Code |
| weight  | _required_, Weight in ounces  |
| mail_class  |  _required_, USPS Service type of: Priority,First Class,Standard Post,Media Mail, Library Mail |
|  container | _optional_, useful for USPS container types, _default_=VARIABLE|
|  size | _optional_, used for USPS weight types, _default_=REGULAR, can be REGULAR or LARGE  |
| length  |  required if size is LARGE, in inches |
|  width |  required if size is LARGE in inches|
|  height | required if size is LARGE  in inches|
|  girth |  required if size is LARGE in inches|

####Sample GET Request with Required Parameters Only
python

```` 
URL = '/label/?o_zip=78756&d_zip=78701&lbs=2'
params={'f_name':'Sophie Hernandez', 'f_address_2':'5310 Joe Sayers Ave Apt 120',\
        'f_city':'Austin','f_state':'TX','f_zip5':78756,'to_name':'Ben','to_address_2':'101 West 6th Street #405','to_city':'Austin',\
        'to_zip5':78701,'to_state':'tx', 'mail_class':'Priority','weight':2}
response = requests.get(URL, params=params)
````
200

#### Sample Response
![link to PDF of label](http://goo.gl/CJMlN6)