from flask import Flask, render_template, Response, request, redirect
import db_functions
import GetFaceWithMesh as GF
from db_functions import *
from choropleth_plotly import HappinessChoropleth


app = Flask(__name__)
choropleth = HappinessChoropleth()


# Homepage met ingave username en start video
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # POST request
        global username, usr_id
        username = request.form["nm"]
        db_functions.db_insert_user(username)
        usr_id = db_functions.db_get_user_id(username)
        return render_template("capture.html")
    else:
        # GET request
        return render_template("index.html")


# Ga naar de pagina om te capturen en vervolgens score te analyzeren
@app.route('/happiness')
def happiness():
    current_img, now = GF.capture(username)
    global result, score, country
    result, score = GF.analyze(current_img)

    # Hier wordt het land bepaald
    country = choropleth.get_happiness_country(score)
    choropleth.load_choropleth(country)
    choropleth.render_html(f"static/{country}")
    db_insert_capture(usr_id, score)
    return render_template('output.html', value=f'{username}_{now}.jpg', result=result)


# Ga naar de pagina waar het resultaat zichtbaar gemaakt wordt
@app.route('/results')
def results():
    return render_template('results.html',
                           countryfile=f"{country}.html",
                           country=country,
                           score=score)


# Ga naar weergave live webcam met landmarks
@app.route('/video_feed')
def video_feed():
    return Response(GF.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=image')


if __name__ == '__main__':
    app.run(debug=True)
