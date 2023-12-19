import os
import yaml
import httpx
import logging
import sched
import time

# logging changes
workspace_folder = os.environ.get('WORKSPACE')
logging.basicConfig(filename=f'{workspace_folder}/reliability_endpoint_test.log',
                    format='%(asctime)s %(message)s', filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
up_out_come = {}
total_runs = {}
availability_percentage = {}


def millis():
    return int(round(time.time() * 1000))


def determine_reliability_of_end_points(scheduler):
    scheduler.enter(15, 1, determine_reliability_of_end_points, (scheduler,))
    logger.debug("determine_reliability_of_end_points")
    config_yaml_file = open("configuration/ReliabilityEndpoints.yml")
    parsed_yaml_file = yaml.load(config_yaml_file, Loader=yaml.FullLoader)
    for entry in parsed_yaml_file['endpoints']:
        input_data = None
        logger.debug("testing" + entry['name'])
        endpoint_url = entry['url']
        if 'body' in entry:
            input_data = entry['body']
        header = {}
        if entry['endpoint'] is not None:
            if "user_agent" in entry['endpoint'][0]:
                header["user_agent"] = entry['endpoint'][0]['user-agent']
        if entry['endpoint'] is not None:
            if "content_type" in entry['endpoint'][0]:
                header["content_type"] = entry['endpoint'][0]["content_type"]
        if 'method' in entry:
            request_method = entry['method']
        else:
            request_method = 'GET'
        start_time = millis()
        response = httpx.request(request_method, url=endpoint_url, data=input_data, headers=header)
        end_time = millis()
        logger.debug("latency for endpoint_url UP -" + endpoint_url + "is (milliseconds) "+str(end_time-start_time))
        if 200 <= response.status_code <= 299:
            if endpoint_url in up_out_come:
                up_out_come[endpoint_url] = up_out_come[endpoint_url] + 1
            else:
                up_out_come[endpoint_url] = 1
            if endpoint_url in total_runs:
                total_runs[endpoint_url] = total_runs[endpoint_url] + 1
            else:
                total_runs[endpoint_url] = 1
        else:
            logger.debug("endpoint_url -" + endpoint_url + "- Failed")
            logger.debug("latency for endpoint_url DOWN -" + endpoint_url + "is (milliseconds) " + str(end_time - start_time))
        if endpoint_url in availability_percentage:
            availability_percentage[endpoint_url] = 100*(up_out_come[endpoint_url]/total_runs[endpoint_url])
            logger.debug(endpoint_url + " has " + availability_percentage[endpoint_url] + " availability percentage ")


if __name__ == '__main__':
    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(15, 1, determine_reliability_of_end_points, (my_scheduler,))
    my_scheduler.run()
