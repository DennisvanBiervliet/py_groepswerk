import pandas as pd
import json
import plotly.express as px
from Lib_db import db_emo


class HappinessChoropleth:
    # Year as input; defaults to 2021
    def __init__(self, year=2021):

        self.year = year

        # Border data loading
        self.borders_path = "input/world.geojson"

        # Automatic world data generation on initialization
        # Creates dataframe from sql database
        self.whr_df = self.world_data_as_pd(self.year)
        # Extract geojson borders data
        self.borders_data = self.open_json_file(self.borders_path)

        # Empty initializing
        self.score = 0
        self.fig = ""

    # Data gathering methods
    def world_data_as_pd(self, year=2021) -> pd.DataFrame:
        """ Method that takes chosen year, queries with it to the SQL database and
        generates a DataFrame with Country name, Ladder score and Year of report
        :param year: Year from the World Happiness Record
        :return: DataFrame with World Happiness Record-scores in a given year
        """

        query = f"""SELECT cou_name as 'Country name',
            hap_score as 'Ladder score',
            yea_year as 'Year'
            FROM countries
            LEFT JOIN world_happiness on world_happiness.hap_cou_id = countries.cou_id
            LEFT JOIN years on world_happiness.hap_yea_id = years.yea_id
            WHERE hap_score IS NOT NULL AND yea_year = {year} 
            """

        cnx, cursor = db_emo.db_load()
        sql_data = pd.read_sql_query(query, cnx)
        db_emo.db_disconnect(cnx, cursor)

        return sql_data

    def open_json_file(self, path: str) -> dict:
        """Method to return json-contents
        :param path: address to geojson-file
        :return: json-contents as a dict
        """
        with open(path) as contents:
            json_data = json.load(contents)

        return json_data

    # Generation of choropleth-figure
    def load_choropleth(self, country="") -> px.choropleth:
        """ Loads choropleth map. If a country is stated, the map will zoom to that country. Else a world map will be
        loaded.
        :param country: countryname as selected by input of happiness score in get_happiness_country()-method
        :return: choropleth object
        """

        if country != "":
            country_json = {"type": self.borders_data["type"],
                            "features":
                                [value for value in self.borders_data["features"] if country in value["properties"]["ADMIN"]]
                            }
        else:
            country_json = self.borders_data

        # Initialization of choropleth
        self.fig = px.choropleth(self.whr_df,
                                 geojson=country_json,
                                 color="Ladder score",
                                 labels={"Ladder score": "Happiness score"},
                                 locations="Country name",
                                 featureidkey="properties.ADMIN",
                                 color_continuous_scale="thermal",
                                 )
        self.fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        self.fig.update_geos(
            resolution=50,
            showcoastlines=True, coastlinecolor="RebeccaPurple",
            showland=True, landcolor="LightGreen",
            showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="LightBlue",
            showcountries=True, countrycolor="Grey",
        )

        # Improve the choropleth legend layout
        if country != "":
            # If land is input: remove legend
            self.fig.update_layout(
                coloraxis_showscale=False,
            )
            self.fig.update_geos(fitbounds="locations")
        else:
            # Standard world choropleth
            lay_out = dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=300, yanchor="top", y=0.8)
            self.fig.update_layout(coloraxis_colorbar=lay_out)

    # Rendering methods of choropleth
    def render_live(self) -> None:
        """This method will automatically render your choropleth in a browser
        :return: None
        """
        if self.fig == "":
            figure = self.load_choropleth()
        else:
            figure = self.fig

        figure.show()

    def render_html(self, path: str) -> None:
        """Method that generates the choropleth as a HTML-file
        :param path: path without extension where the HTML-file will be created
        :return: None
        """
        if self.fig == "":
            figure = self.load_choropleth()
        else:
            figure = self.fig

        figure.write_html(f"{path}.html")

    def render_image_svg(self, path: str):
        """Method that generates the choropleth as a HTML-file
        :param path: path without extension where the SVG-file will be created
        :return: None
        """
        if self.fig == "":
            figure = self.load_choropleth()
        else:
            figure = self.fig

        self.fig.write_image(f"{path}.svg")

    # Country score algorithm
    def get_happiness_country(self, score: float):
        """ Method that uses your inputted score to seek in the database the country
        closest to your input
        :param score: (float) calculated happiness score
        :return: (str) country closest to your calculated happiness score
        """
        # Get index from the country which has the closest happiness to input
        index = abs(self.whr_df['Ladder score'] - score).idxmin()

        # Returns country with calculated index
        return self.whr_df.iloc[index]["Country name"]

    # Methods not used anymore
    def _generate_countries_list(self) -> list:
        """ Generates a list of all the countries from the geojson-file.
        Was used to generate a countries database in SQL
        :return (list): Returns a list of countries
        """
        q_countries = len(self.borders_data["features"])
        countries = []

        for i in range(q_countries):
            countries.append(self.borders_data["features"][i]["properties"]["ADMIN"])

        return countries

    def _read_excel_as_pd(self, path) -> pd.DataFrame:
        """Method that creates a DataFrame from an excel-file.
        Used for filling tables in database
        :param path: address to excel to create DataFrame from
        :return: DataFrame
        """
        return pd.read_excel(path)

    def __str__(self):
        if self.fig == "":
            return f"""Choropleth-data {self.year}: <EMPTY>"""
        else:
            return f"""Choropleth-data {self.year}: <LOADED>"""
