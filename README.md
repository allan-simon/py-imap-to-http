# py-imap-to-http
async service that will check an imap folder and send them to an http service

### Dev environment

If you want to test it / modify it in a clean environment
There's one provided (if you have `docker` and `vagrant` on your machine), it's as simple then as doing

```sh
vagrant up
vagrant ssh
```

### Use it

You can either use the docker image

```
docker push allansimon/py-imap-to-http
```

or run the project using

```sh
python3 -m service
```

it will check your INBOX (or other folder you've configured), iterate over the emails,
POST a http form (with attachments if any) to the specified url.

In case your http service responsed a 2XX, it will then move the email to a `success` folder, otherwise it will move it to a `error` (both can be configured)

It will also treat emails as soon as they are received in an efficient manner (using the `IDLE` capacity of IMAP and not some ugly `sleep` hacks)

### Environment variables

 * `IMAP_SERVER` : imap server to check (e.g `imap.gmail.com`)
 * `IMAP_USER` : user to use to connect to the imap (e.g `your.user@gmail.com`)
 * `IMAP_PASSWORD` : user's password  (e.g `your.user@gmail.com`)
 * `IMAP_CHECK_FOLDER`: folder to observe (by default `INBOX`)
 * `IMAP_SUCCESS_FOLDER`: email treated successfully will be moved there
 * `IMAP_ERROR_FOLDER`: email treated with errors will be moved there
 * `IMAP_POST_TO_URL`: the emails will be POSTed one by one to this address as if you had submitted a HTML form.


### POST url fields

The `IMAP_POST_TO_URL` should be able to treat a multipart/url-encoded POST (i.e traditional HTML form, like it's the 90s all over again, why reinventing the wheel...) with the following form's fields:

   * `from`: the email it's from
   * `to`: the email it's from
   * `date`: an ISO 8601 formatted datetime of the email's Date header
   * `message_id`: the imap server's id associated to the email
   * `body`: the plain text body

   in case of attachments you will have the following additional fields:

   * `attachments[0]` , `attachments[1]` etc.

### PR / Issues are welcomed

If you want an additional fields to be treated, or if you want the POST to be configured to be a `PUT`, or to submit it as JSON/XML/etc. feel free to open a merge request
