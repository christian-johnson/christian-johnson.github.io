import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime
import pytz
from datetime import timedelta
from vega_datasets import data
from pyodide.http import open_url

# needed to plot >5k points without vegafusion
alt.data_transformers.disable_max_rows()
alt.renderers.enable("default")

# Get around CORS restrictions on NOAA server
proxy_url = "https://corsproxy.io/?"


def get_latest_gfs(max_lookback_hours=12):
    # Figure out which GFS run we want to query
    # GFS runs every 6 hours, with hourly forecasts
    eastern = pytz.timezone("US/Eastern")
    current_eastern_time = datetime.now(eastern)
    # Round down to the nearest 6-hour mark
    offset = current_eastern_time.hour % 6
    gfs_time = current_eastern_time.replace(
        minute=0, second=0, microsecond=0
    ) - timedelta(hours=offset)

    for _ in range(0, max_lookback_hours, 6):
        year = gfs_time.year
        month = f"{gfs_time.month:02}"
        day = f"{gfs_time.day:02}"
        hour = f"{gfs_time.hour:02}"
        temp_url = f"https://nomads.ncep.noaa.gov/dods/gfs_1p00/gfs{year}{month}{day}/gfs_1p00_{hour}z.ascii?tmp2m[0:1:0][0:1:179][0:1:359]"
        pres_url = f"https://nomads.ncep.noaa.gov/dods/gfs_1p00/gfs{year}{month}{day}/gfs_1p00_{hour}z.ascii?pressfc[0:1:0][0:1:179][0:1:359]"
        try:
            s = open_url(proxy_url + temp_url).read()
            p = open_url(proxy_url + pres_url).read()

            lons = np.array(s.split("\n")[-2].split(", "), dtype=float)
            lats = np.array(s.split("\n")[-4].split(", "), dtype=float)

            df = pd.concat(
                [
                    pd.DataFrame(
                        {
                            "lat": lats[i],
                            "lon": lons,
                            "tmp2m": np.array(
                                s.split("\n")[i + 1].split(", ")[1:], dtype=float
                            ),
                            "press": np.array(
                                p.split("\n")[i + 1].split(", ")[1:], dtype=float
                            ),
                        }
                    )
                    for i in range(len(lats))
                ],
                axis=0,
            )
            df["tmp2m"] -= 273.15
            df["press"] *= 9.868 * 10 ** (-6)
            return df
        except:
            print("no GFS data for:", hour)
            gfs_time -= timedelta(hours=6)

    raise RuntimeError("No available GFS datasets found in the given lookback window.")


def find_matching_antipodes(df):
    """Get the antipode locations with equal temperature & pressure."""
    threshold = 0.001

    # Create antipode coordinates
    df = df.copy()
    df["antipode_lat"] = -df["lat"]
    df["antipode_lon"] = (df["lon"] + 180) % 360

    # Merge with itself on antipodal coordinates
    merged = df.merge(
        df,
        left_on=["antipode_lat", "antipode_lon"],
        right_on=["lat", "lon"],
        suffixes=("", "_opp"),
    )

    # Compute differences
    merged["tmp2m_diff"] = (merged["tmp2m"] - merged["tmp2m_opp"]) / merged["tmp2m"]
    merged["press_diff"] = (merged["press"] - merged["press_opp"]) / merged["press"]

    # Apply threshold condition
    equals = merged[
        (np.abs(merged["tmp2m_diff"]) < threshold)
        & (np.abs(merged["press_diff"]) < threshold)
    ]
    print(len(equals))

    # Optionally, return only the original columns
    return equals[df.columns]


def generate_plot(df, match_df):
    # Interactive rotation slider
    range0 = alt.binding_range(min=0, max=360, step=1, name="Rotate Longitude ")
    rotate0 = alt.param(value=0, bind=range0)

    # Dropdown to select variable
    dropdown = alt.binding_select(options=["tmp2m", "press"], name="Variable to plot ")
    var_param = alt.param(value="tmp2m", bind=dropdown)

    # Base sphere (drawn last as a clipping mask)
    sphere = alt.Chart(alt.sphere()).mark_geoshape(
        fill=None, stroke="white", strokeWidth=8.0
    )

    points = (
        alt.Chart(df)
        .transform_calculate(
            lon="datum.lon",
            lat="datum.lat",
            # angular distance from center (cosine approximation)
            cos_angle=f"cos((datum.lon - (360 - {rotate0.name})) * PI / 180)",
            angle_to_edge=f"cos((datum.lon - (360 - {rotate0.name})) * PI / 180) * sin((datum.lat + 90) * PI / 180)",
            value=f"datum[{var_param.name}]",
            label_value=f"{var_param.name} + ': ' + format(datum[{var_param.name}], '.2f')",
            lat_value="'lat'",
        )
        .transform_filter(
            # Only show front-facing hemisphere (cos_angle > 0)
            "datum.cos_angle > 0"
        )
        .mark_circle()
        .encode(
            longitude="lon:Q",
            latitude="lat:Q",
            color=alt.Color(
                "value:Q",
                scale=alt.Scale(
                    scheme="redyellowblue",
                    reverse=True,
                    domain={
                        "expr": f"{var_param.name} === 'tmp2m' ? [-50, 50] : "
                        + f"{var_param.name} === 'press' ? [0.5, 1.1] : [0, 1]"
                    },
                ),
            ),
            # simulate 3D perspective by reducing size based on cosine angle
            size=alt.Size(
                "angle_to_edge:Q",
                scale=alt.Scale(domain=[0, 1], range=[5, 100]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("label_value:N", title=" "),
            ],
        )
        .add_params(rotate0, var_param)
    )

    matches = (
        alt.Chart(match_df)
        .transform_calculate(
            lon="datum.lon",
            lat="datum.lat",
            # angular distance from center (cosine approximation)
            cos_angle=f"cos((datum.lon - (360 - {rotate0.name})) * PI / 180)",
            angle_to_edge=f"cos((datum.lon - (360 - {rotate0.name})) * PI / 180) * sin((datum.lat + 90) * PI / 180)",
            value=f"datum[{var_param.name}]",
            label_value=f"{var_param.name} + ': ' + format(datum[{var_param.name}], '.2f')",
            lat_value="'lat'",
        )
        .transform_filter(
            # Only show front-facing hemisphere (cos_angle > 0)
            "datum.cos_angle > 0.2"
        )
        .mark_circle(
            color="violet",  # fill color
            stroke="black",  # border color
            strokeWidth=1.5,  # border thickness
            size=100,  # point size
        )
        .encode(
            longitude="lon:Q",
            latitude="lat:Q",
            tooltip=[
                alt.Tooltip("label_value:N", title=" "),
            ],
        )
        .add_params(rotate0, var_param)
    )

    # Land boundaries (on top of points)
    land = (
        alt.Chart(alt.topo_feature(data.world_110m.url, "countries"))
        .mark_geoshape(fill=None, stroke="black")
        .add_params(rotate0)
    )

    # Land boundaries (on top of points)
    land = (
        alt.Chart(alt.topo_feature(data.world_110m.url, "countries"))
        .mark_geoshape(fill=None, stroke="black")
        .add_params(rotate0)
    )

    # Final composition: draw sphere last to act as visual mask
    chart = (
        alt.layer(points, land, matches, sphere)
        .project(
            type="orthographic",
            rotate=alt.expr(f"[{rotate0.name}, 0.1, 0]"),
        )
        .properties(width=500, height=500)
        .properties(background="white")
    ).configure_legend(disable=True)
    return chart.to_json()


def select_random_opposite_pair(df):
    # pick random row
    row0 = np.random.choice(np.arange(len(df)))
    # find its pair
    row1 = np.where(
        np.logical_and(
            df.iloc[row0]["lat"] == df["antipode_lat"],
            df.iloc[row0]["lon"] == df["antipode_lon"],
        )
    )[0][0]
    return [row0, row1]


# Load data on page load
df = get_latest_gfs()
# Find antipode pairs
match_df = find_matching_antipodes(df)


# Pick a pair at random and draw it when the user clicks the button
def generate_chart(df=df, match_df=match_df):
    ilocs = select_random_opposite_pair(match_df)
    return generate_plot(df, match_df.iloc[ilocs])
