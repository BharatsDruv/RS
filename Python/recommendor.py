# import necessary libraries and functions
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin


class Recommendor:

    # Contains chronological list of best possible values of qos throughout the data
    global top_list 

    # Contains chronological list of best possible values of qos throughout the data
    global bottom_list

    # Contains total number of qos parameters per web service
    global number_of_qos

    # Contains whether high value is better or low for the particular qos
    # -1 means on increasing value qos denotes worse value
    # 1 means on increasing value qos denotes better value
    global qos_order

    def __init__(self, services_list_file):
        self.qos_order = [-1, 1, 1, 1, 1, 1, 1, -1]
        self.number_of_qos = 8
        self.getTopBottomList(services_list_file)

    # generates top_list and bottom_list
    # param:
    # services_list_file: a file containing the qos parameters of various web services
    def getTopBottomList(self, services_list_file):

        # open file
        with open(services_list_file) as file:
            services_qos_list = file.readlines()

            # get top and bottom list
            self.top_list = list(map(float, services_qos_list[0].split(",").copy()))

            self.bottom_list = list(map(float, services_qos_list[0].split(",").copy()))
            for line_index in range(1,len(services_qos_list)):
                qos_list = list(map(float, services_qos_list[line_index].split(",")))

                for qos_index in range(self.number_of_qos):
                    self.top_list[qos_index] = max(self.top_list[qos_index], qos_list[qos_index])
                    self.bottom_list[qos_index] = min(self.bottom_list[qos_index], qos_list[qos_index])
        # swap top and bottom list of invert qos
        if self.qos_order[qos_index] == -1:
            self.top_list[qos_index], self.bottom_list[qos_index] = self.bottom_list[qos_index], self.top_list[qos_index]

    # normalizes the single qos value such that:
    # 1. qos value ranges from 0 to 1(inclusive)
    # 2. value 1 means best and 0 means worst case
    # params:
    # top: best available value of qos in dataset
    # bottom: worst available value of qos in dataset
    # value: value of qos for current web service
    # returns:
    # normalized value of qos
    def normalizeSingleValue(self, top, bottom, value):
   
        margin = min(top, bottom)
        value -= margin
        top -= margin
        bottom -= margin   
       
        if top < bottom:
            value = bottom - value
            top, bottom = bottom, top
        if value < bottom or value > top:
            return -1
        else:
            return value/top;

    # normalizes the list of qos for a single web service such that:
    # 1. each value ranges from 0 to 1(inclusive)
    # 2. value 1 means best and 0 means worst case
    # params:
    # qos_list: list of qos for a single web service
    # returns:
    # normalized list of qos
    def normalizeListOfQos(self, qos_list):
        normalizedValueList = []
        for top, bottom, value in zip(self.top_list, self.bottom_list, qos_list):
            normalizedValueList.append(self.normalizeSingleValue(top, bottom, value))
           
        return normalizedValueList


    # recommends best k services among the dataset as per user's preference
    # params:
    # services_list_file: a file containing the qos parameters of various web services
    # services_name_file: a file containing the qos parameters along with the names of web services
    # list_of_weights: chronological list of weights assigned to each qos according to user's preference
    # k: number of weights to be recommended
    # returns:
    # names of recommended services
    def recommendBestK(self, services_list_file, services_name_file, list_of_weights, k):
       
        personalized_services_qos_list = []
       
        with open(services_list_file) as file:

            # convert file into list
            services_qos_list = file.readlines()

            # normalize and personalize the whole list
            for line_index in range(len(services_qos_list)):
                qos_list = list(map(float, services_qos_list[line_index].split(",")))

                # normalize single row
                services_qos_list[line_index] = self.normalizeListOfQos(qos_list)
                personalized_qos_list = []

                # personalize single row
                for qos, weight in zip(services_qos_list[line_index], list_of_weights):
                    personalized_qos_list.append(qos*weight)
                personalized_services_qos_list.append(personalized_qos_list)

            # add indices to each personalized row
            for line_index in range(len(personalized_services_qos_list)):
                personalized_services_qos_list[line_index].append(line_index)

            # sort according to personalized weights of each service
            personalized_services_qos_list.sort(reverse=True, key = lambda personalized_qos_list: sum(personalized_qos_list[:-1]))

            # collect indices of best k according to user preference
        recommended_services_indices = [personalized_qos_list[-1] for personalized_qos_list in personalized_services_qos_list]
        recommended_services_indices = recommended_services_indices[:min(20,k)]

        # fetch names of recommended services and return
        recommended_services_names = self.getNamesListByIndices(services_name_file, recommended_services_indices)
        return recommended_services_names

    def getNamesListByIndices(self, services_name_file, indices_list):

        names_list = []

        with open(services_name_file) as file:
            file_lines = file.readlines()
            for index in indices_list:
                required_line = file_lines[index]
                required_line = required_line.split(',')
                name = required_line[-1]
                names_list.append(name)

        return names_list


# Using flask to make an api
  
# creating a Flask app
app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/test', methods=['POST'])
@cross_origin()
def index():
    # headers = {"Content-Type": "text/plain","Accept":"text/plain"}
    # values = list(map(int,request.form.get('values').split()))
    print(request.data)
    return request.data
    # return "<h1>Welcome to our server !!</h1>"
  
# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/post', methods = ['POST'])
def home():
    values = list(map(int,request.form.get('values').split()))
    recommendor = Recommendor("services_list_file.txt")
    name_list = recommendor.recommendBestK("services_list_file.txt", "services_name_file.txt", values[1:], values[0])
    # result = "{\n"
    # for index in range(len(name_list)):
    #     result += name_list[index] + "\n"
    # result += "}"
    return jsonify(name_list)

# driver function
if __name__ == '__main__':
  
    app.run(debug = True)
