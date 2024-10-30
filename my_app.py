from flask import Flask, render_template, request, jsonify
import requests
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

map_list = [
    [25.0397146, 121.5653771],
    [25.0405919, 121.5647644],
    [25.039982, 121.572258],
    [25.0336076, 121.5647587],
    [25.033263, 121.560492],
    [25.0400306, 121.5602452]
]

chinese_address_list = [
    "110台北市信義區松高路9號",
    "110台北市信義區忠孝東路五段8號5樓",
    "110台北市信義區忠孝東路五段236巷15號",
    "110台北市信義區信義路五段7號",
    "110台灣信義區信義路五段1號",
    "110台北市信義區仁愛路四段505號"
]

orig_list = []
dest_list = []

# Haversine formula to calculate distance between two points on Earth
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in kilometers

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Calculate differences between latitudes and longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Calculate distance using Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # Distance in kilometers
    return distance


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'new_address' in request.form:  # upload_location
            # 接收使用者上傳的位置
            address = request.form['new_address']

            # 使用 Google 地理編碼 API 取得該地址的經緯度
            google_api_key = 'AIzaSyDcI0vxTU33OBI8IlG5UUjeOtEvbg9Fh2g'
            addurl = f'https://maps.googleapis.com/maps/api/geocode/json?key={google_api_key}&address={address}&sensor=false'
            addressReq = requests.get(addurl)
            addressDoc = addressReq.json()

            # 取得地址對應的經緯度
            new_lat = addressDoc['results'][0]['geometry']['location']['lat']
            new_lon = addressDoc['results'][0]['geometry']['location']['lng']

            # 將新位置添加到 map_list
            map_list.append([new_lat, new_lon])

            # 再將經緯度轉換為中文地址
            addurl2 = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={new_lat}, {new_lon}&language=zh-TW&key={google_api_key}'
            addressReq2 = requests.get(addurl2)
            addressDoc2 = addressReq2.json()
            new_location = addressDoc2['results'][0]['formatted_address']

            # 將新位置添加到 chinese_address_list
            chinese_address_list.append(new_location)

            return render_template('index.html', chinese_address_list=chinese_address_list, map_list=map_list)
        elif ('origin' in request.form):
            orig = request.form['origin']
            dest = request.form['destination']

            google_api_key = 'AIzaSyDcI0vxTU33OBI8IlG5UUjeOtEvbg9Fh2g'
            
            origURL = f'https://maps.googleapis.com/maps/api/geocode/json?key={google_api_key}&address={orig}&sensor=false'
            destURL = f'https://maps.googleapis.com/maps/api/geocode/json?key={google_api_key}&address={dest}&sensor=false'

            origRessReq = requests.get(origURL)
            destRessReq = requests.get(destURL)
            origRessDoc = origRessReq.json()
            destRessDoc = destRessReq.json()

            orig_lat = origRessDoc['results'][0]['geometry']['location']['lat']
            orig_lon = origRessDoc['results'][0]['geometry']['location']['lng']
            dest_lat = destRessDoc['results'][0]['geometry']['location']['lat']
            dest_lon = destRessDoc['results'][0]['geometry']['location']['lng']


            orig_list.append(orig_lat)
            orig_list.append(orig_lon)
            dest_list.append(dest_lat)
            dest_list.append(dest_lon)

            return render_template('index.html', map_list=map_list, orig_list=orig_list, dest_list=dest_list)
        
        else:
            address = request.form['current_address']
            google_api_key = 'AIzaSyDcI0vxTU33OBI8IlG5UUjeOtEvbg9Fh2g'  # 請將此處替換為您自己的 Google API 金鑰

            addurl = f'https://maps.googleapis.com/maps/api/geocode/json?key={google_api_key}&address={address}&sensor=false'
            addressReq = requests.get(addurl)
            addressDoc = addressReq.json()

            current_lat = addressDoc['results'][0]['geometry']['location']['lat']
            current_lon = addressDoc['results'][0]['geometry']['location']['lng']

            # Calculate distances to each accident location and find the closest one
            min_distance = float('inf')
            closest_location = None

            for i in range(len(map_list)):
                accident_lat = map_list[i][0]
                accident_lon = map_list[i][1]
                distance = calculate_distance(current_lat, current_lon, accident_lat, accident_lon)

                if distance < min_distance:
                    min_distance = distance
                    closest_location = map_list[i]

            # 最接近災害位置的經緯度轉中文地址
            result_lat = closest_location[0]
            result_lon = closest_location[1]
            # 在下面經緯度後面加入&language=zh-TW，可以把地址變中文
            addurl3 = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={result_lat}, {result_lon}&language=zh-TW&key={google_api_key}'
            addressReq3 = requests.get(addurl3)
            addressDoc3 = addressReq3.json()
            closest_location = addressDoc3['results'][0]['formatted_address']

            closest_location_info = f"最接近的災害地點: {closest_location}"
            distance_info = f"離你現在位置大約 {min_distance:.2f} 公里"

            return render_template('index.html', map_list=map_list, closest_location_info=closest_location_info,
                                   distance_info=distance_info, chinese_address_list=chinese_address_list, orig_list=orig_list, dest_list=dest_list)
    
    return render_template('index.html', map_list=map_list, chinese_address_list=chinese_address_list)
    # return render_template('index.html', address_list=address_list)

@app.route('/get_variable')
def get_variable():
    return jsonify({'variable': map_list, 'variable2': chinese_address_list})

@app.route('/get_route')
def get_route():
    return jsonify({'o': orig_list, 'd': dest_list})

if __name__ == '__main__':
    app.run(debug=True)