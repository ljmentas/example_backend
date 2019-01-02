from datetime import date
import boto3
import redis
import random
import json


#TODO: this should be config
sqs = boto3.client('sqs',"us-east-1")
#TODO: this should be config
queue = sqs.get_queue_url(QueueName='terraform-example-queue')
test_queue_url= queue["QueueUrl"]
#TODO: this should be config
redis_client = redis.Redis(host='cluster-demo.gthbrr.0001.use1.cache.amazonaws.com', port=6379, db=0)

class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = {'version': '3.5.1',
                    'last_build': date.today().isoformat()}
        self.write(response)


class send_sqs_message(tornado.web.RequestHandler):
    #TODO: this should be removed after buying a new route53 entry
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", 'x-requested-with, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Cache-control", "no-cache")

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    def post(self):
        # needs json validation
        # error handing???
        enqueue_response = sqs.send_message(QueueUrl=test_queue_url, MessageBody=str(self.request.body))
        data_id = enqueue_response['MessageId']
        self.set_status(202)
        response = {'message_id': data_id,
                    'date': date.today().isoformat()}
        self.write(response)


class get_finished_job(tornado.web.RequestHandler):

    #TODO: this should be removed after buying a new route53 entry
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", 'x-requested-with, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Cache-control", "no-cache")

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    def get(self,job_id):

        value = redis_client.get(job_id)
        if value == None:
            response = {'message': 'job not complete'}
        else:
            response = {'result': value}
            self.write(response)

application = tornado.web.Application([
    (r"/enqueuejob", send_sqs_message),
    (r"/getjob/([^/]*)", get_finished_job),
    (r"/version", VersionHandler)
])

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
