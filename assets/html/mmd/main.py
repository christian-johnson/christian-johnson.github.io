import altair as alt
from vega_datasets import data
from pyodide.http import open_url
import numpy as np
import networkx as nx
import pandas as pd
import geopandas as gpd
import json

# Configure Altair for Vega-Embed
alt.renderers.enable("default")

# Pre-load state FIPS mapping for reuse
state_fips_map = {
    "Alabama": "1",
    "Alaska": "2",
    "Arizona": "4",
    "Arkansas": "5",
    "California": "6",
    "Colorado": "8",
    "Connecticut": "9",
    "Delaware": "10",
    "District of Columbia": "11",
    "Florida": "12",
    "Georgia": "13",
    "Hawaii": "15",
    "Idaho": "16",
    "Illinois": "17",
    "Indiana": "18",
    "Iowa": "19",
    "Kansas": "20",
    "Kentucky": "21",
    "Louisiana": "22",
    "Maine": "23",
    "Maryland": "24",
    "Massachusetts": "25",
    "Michigan": "26",
    "Minnesota": "27",
    "Mississippi": "28",
    "Missouri": "29",
    "Montana": "30",
    "Nebraska": "31",
    "Nevada": "32",
    "New Hampshire": "33",
    "New Jersey": "34",
    "New Mexico": "35",
    "New York": "36",
    "North Carolina": "37",
    "North Dakota": "38",
    "Ohio": "39",
    "Oklahoma": "40",
    "Oregon": "41",
    "Pennsylvania": "42",
    "Rhode Island": "44",
    "South Carolina": "45",
    "South Dakota": "46",
    "Tennessee": "47",
    "Texas": "48",
    "Utah": "49",
    "Vermont": "50",
    "Virginia": "51",
    "Washington": "53",
    "West Virginia": "54",
    "Wisconsin": "55",
    "Wyoming": "56",
}


def load_and_format_dataframe(state):
    # Load shapefile from GeoJSON
    geojson_input = data.us_10m.url
    with open_url(geojson_input) as f:
        df_shp = gpd.read_file(f, layer="counties")
    df_shp = df_shp[df_shp["id"].apply(lambda x: x[:-3]) == state_fips_map[state]]
    df_shp["FIPS"] = df_shp["id"].apply(int)
    df_shp = df_shp[["FIPS", "geometry"]]
    df_shp["geometry"] = df_shp["geometry"].buffer(0)
    # Filter down to state of interest first, to save merging time later

    # Load 2020 election results from Election Atlas CSV
    filename = "data/2020_election_results.csv"
    with open_url(filename) as f:
        df_election = pd.read_csv(f)
    df_election = df_election[["FIPS", "Joseph R. Biden Jr.", "Donald J. Trump"]]
    df_election.columns = ["FIPS", "DEM", "GOP"]
    df_election = df_election.iloc[1:]
    df_election["FIPS"] = df_election["FIPS"].astype("int")
    df_election["DEM"] = df_election["DEM"].astype("int")
    df_election["GOP"] = df_election["GOP"].astype("int")
    df_election = df_election.merge(df_shp, left_on=["FIPS"], right_on=["FIPS"])

    # Load Population data from Census CSV
    filename = "data/2020_census_population_by_county.csv"
    with open_url(filename) as f:
        df_pop = pd.read_csv(f, skiprows=[0])
    df_pop["FIPS"] = df_pop["Geography"].apply(lambda x: int(x.split("US")[1]))
    df_pop = df_pop[["FIPS", " !!Total", "Geographic Area Name"]]
    df_pop = df_pop.rename(
        {" !!Total": "population", "Geographic Area Name": "County"}, axis=1
    )

    # Join election data into the dataframe
    df_pop = df_pop.merge(df_election, how="inner", left_on="FIPS", right_on="FIPS")

    # Result is one single dataframe for our state, with geometry, population
    # and election results all together
    return gpd.GeoDataFrame(df_pop)


def compute_adj_matrix(gdf, min_length=0.1):
    """Given a GeoDataFrame, compute the adjacency matrix.

    Sometimes, two geometries will be kitty-corner to each other.
    For that reason, we actually decide if something is adjacent
    by whether their common length is longer than a threshold min_length
    """
    n = len(gdf)
    adj = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                if (
                    gdf.iloc[i]["geometry"].intersection(gdf.iloc[j]["geometry"]).length
                    > min_length
                ):
                    adj[i, j] = 1
    graph = nx.Graph(adj)
    return adj, graph


class Districter:
    def __init__(
        self,
        state,
        num_districts,
        tolerance,
        min_reps,
        n_representatives,
        column="population",
    ):
        """Initialize the Districter class.

        Initialization here means to load the dataframes needed, ensure
        that the parameters chosen are okay, and compute the adjacency matrix."""

        self.df = load_and_format_dataframe(state)
        self.adj_matrix, self.graph = compute_adj_matrix(self.df)
        self.impossible = False
        self.tolerance = 0.01 * float(tolerance)  # input as percent
        self.n = len(self.df)
        self.n_iterations = 20
        self.n_representatives = int(n_representatives)
        self.n_attempts = 10

        if int(num_districts) > self.n - 1:
            raise Exception("Number of districts must be less than number of counties")
        else:
            self.num_districts = int(num_districts)

        self.metric = self.df[column].values

        self.min_reps = int(min_reps)
        # Maximum reps per district is however many the largest county on its own would get
        self.max_reps = round(
            self.n_representatives * np.max(self.metric) / np.sum(self.metric)
        )
        self.ideal_district_size = np.sum(self.metric) / self.n_representatives

        self.representativeness = (
            self.metric / np.sum(self.metric) * self.n_representatives
        )
        self.representativeness -= np.floor(self.representativeness)
        self.initialize_districts()

    def initialize_districts(self):
        self.impossible = False
        self.districts = np.zeros((self.n))

        # Randomly assign initial districts

        self.districts[
            np.random.choice(np.arange(self.n), size=self.num_districts, replace=False)
        ] = 1 + np.arange(self.num_districts)
        # Grow the components randomly until there are no district 0s left anymore
        while np.any(self.districts == 0):
            choice1 = np.random.choice(np.where(self.districts == 0)[0], size=1)
            neighbors = np.where(self.adj_matrix[choice1, :].flatten())[0]
            different_neighbors = neighbors[np.where(self.districts[neighbors] != 0)[0]]
            if len(different_neighbors) > 0:
                self.districts[choice1] = self.districts[
                    np.random.choice(different_neighbors, size=1)
                ]

    def collapse_graph_by_label(self, G):
        # Create a new graph
        new_G = nx.Graph()
        # Create a dictionary to map labels to nodes

        # Iterate over the nodes in the original graph
        for node in G.nodes():
            # Get the label for the current node
            label = G.nodes[node]["district"]

            # If this label hasn't been seen before, add a new node to the new graph
            if label not in new_G.nodes:
                new_G.add_node(label)

            # Add edges to the new graph based on the edges in the original graph
            for neighbor in G.neighbors(node):
                neighbor_label = G.nodes[neighbor]["district"]
                if neighbor_label != label:
                    # If the neighbor has a different label, create an edge in the new graph
                    new_G.add_edge(label, neighbor_label)

        return new_G

    def recom_step(self):
        """
        Use recombination MC method to assign new districts
        """

        # Select two adjacent districts
        collapsed_G = self.collapse_graph_by_label(self.graph)
        collapsed_edges = np.array([e for e in collapsed_G.edges])
        random_edge = np.random.choice(np.arange(len(collapsed_edges)))
        district1 = collapsed_edges[random_edge][0]
        district2 = collapsed_edges[random_edge][1]

        total_reps = self.reps[district1 - 1] + self.reps[district2 - 1]
        total_pop = self.pops[district1 - 1] + self.pops[district2 - 1]

        # Combine them into one graph
        g = nx.subgraph(
            self.graph,
            np.array(
                [
                    n
                    for n in self.graph.nodes
                    if self.graph.nodes[n]["district"] in [district1, district2]
                ]
            ),
        )

        # Find the minimal spanning tree
        spanning_tree = nx.algorithms.minimum_spanning_tree(g)
        spanning_tree_edges = np.array([e for e in spanning_tree.edges])

        possible_edge_removals = {}
        # Loop through possible edge cuts
        for i, e in enumerate(spanning_tree_edges):
            possible_edge_removals[i] = 0
            g_ = spanning_tree.copy()
            g_.remove_edge(e[0], e[1])
            reps = 0
            pop = 0
            for j, newdistrict in enumerate(nx.connected_components(g_)):
                pop = np.sum(self.metric[np.array(list(newdistrict))])
                if j == 0:
                    reps = round(
                        np.clip(
                            total_reps * pop / total_pop,
                            a_min=self.min_reps,
                            a_max=min(self.max_reps, total_reps - self.min_reps),
                        )
                    )
                else:
                    reps = total_reps - reps
                possible_edge_removals[i] += np.abs(
                    pop / reps - self.ideal_district_size
                )

        # Pick the best edge to cut
        best_edge = np.argmin(np.array(list(possible_edge_removals.values())))

        # Reassign counties
        spanning_tree.remove_edge(
            spanning_tree_edges[best_edge][0], spanning_tree_edges[best_edge][1]
        )
        components = np.array(list(nx.connected_components(spanning_tree)))
        self.districts[np.array(list(components[0]))] = district1
        self.districts[np.array(list(components[1]))] = district2

    def smart_assign(self, old_flip=None, verbose=False):
        # Loop through all counties
        possible_flips = []
        for county in range(self.n):
            # Identify possible flips by looking at the neighbors of each county
            for neighbor in self.graph.neighbors(county):
                if self.districts[neighbor] != self.districts[county]:
                    G = self.graph.copy()
                    # We can't disconnect any districts
                    # Identify the correct subgraph
                    node_to_district = dict(zip(range(self.n), self.districts))
                    G.remove_node(county)

                    # Find the subgraph of G where the nodes have the same integer as X did
                    subgraph_nodes = [
                        node
                        for node, integer in node_to_district.items()
                        if integer == node_to_district[county]
                    ]
                    subgraph = G.subgraph(subgraph_nodes)

                    if len(subgraph) > 0:
                        if nx.is_connected(subgraph):
                            possible_flips.append(
                                {
                                    "county": county,
                                    "from": self.districts[county],
                                    "to": self.districts[neighbor],
                                }
                            )

        # Loop through possible flips to find the most advantageous one:
        for flip in possible_flips:
            # How many reps do we need to reallocate?
            old_from_reps = self.reps[int(flip["from"]) - 1]
            old_to_reps = self.reps[int(flip["to"]) - 1]
            reps = old_from_reps + old_to_reps

            # Compute new populations of the "from" and "to" districts
            old_from_pop = np.sum(self.metric[np.where(self.districts == flip["from"])])
            old_to_pop = np.sum(self.metric[np.where(self.districts == flip["to"])])

            new_from_pop = old_from_pop - self.metric[flip["county"]]
            new_to_pop = old_to_pop + self.metric[flip["county"]]

            # total population doesn't change, of course
            total_pop = old_from_pop + old_to_pop

            # reallocate representatives for the 2 new districts
            if new_from_pop > new_to_pop:
                new_from_reps = int(
                    np.round(
                        np.clip(
                            reps * new_from_pop / total_pop,
                            a_min=self.min_reps,
                            a_max=min(self.max_reps, reps - self.min_reps),
                        )
                    )
                )
                new_to_reps = reps - new_from_reps
            else:
                new_to_reps = int(
                    np.round(
                        np.clip(
                            reps * new_to_pop / total_pop,
                            a_min=self.min_reps,
                            a_max=min(self.max_reps, reps - self.min_reps),
                        )
                    )
                )
                new_from_reps = reps - new_to_reps

            # compute whether absolute difference from ideal has improved or not
            old_from_diff = np.abs(
                old_from_pop / old_from_reps - self.ideal_district_size
            )
            old_to_diff = np.abs(old_to_pop / old_to_reps - self.ideal_district_size)

            new_from_diff = np.abs(
                new_from_pop / new_from_reps - self.ideal_district_size
            )
            new_to_diff = np.abs(new_to_pop / new_to_reps - self.ideal_district_size)

            flip["diff"] = (old_from_diff + old_to_diff) ** 2 - (
                new_from_diff + new_to_diff
            ) ** 2

        # TODO or make any one district have too many reps

        # make the best flip
        best_flip = np.argmax([f["diff"] for f in possible_flips])

        if old_flip is not None:
            if (
                old_flip["county"] == possible_flips[best_flip]["county"]
                and old_flip["from"] == possible_flips[best_flip]["to"]
            ):
                best_flip = np.argsort([f["diff"] for f in possible_flips])[::-1][
                    np.random.choice(np.arange(1, 10))
                ]

        self.districts[possible_flips[best_flip]["county"]] = possible_flips[best_flip][
            "to"
        ]
        return possible_flips[best_flip]

    def iterate_districts(self):
        """
        Find a candidate swap to do:
        Choose from the most over-represented district, and give to a less-represented neighbor
        (That's the neighborly thing to do!)
        But, go to the next-most over-represented district if there's only 1 county (and so on)
        """

        biggest_districts = np.argsort(self.evaluate_districts())[::-1]
        i = 0
        biggest_district = biggest_districts[i] + 1
        while (
            len(np.where(self.districts == biggest_district)[0]) == 1
            or len(
                np.where(
                    self.representativeness[
                        np.where(self.districts == biggest_district)
                    ]
                    > np.mean(self.representativeness)
                )[0]
            )
            < 2
        ):
            i += 1
            biggest_district = biggest_districts[i] + 1
        self.evaluate_districts()

        # Only do this if the donated county is going to be above average in its representativeness
        choice1 = np.random.choice(
            np.where(
                np.logical_and(
                    self.districts == biggest_district,
                    self.representativeness > np.mean(self.representativeness),
                )
            )[0],
            size=1,
        )

        # Find out which (if any) of its neighbors are in a different district
        neighbors = np.where(self.adj_matrix[choice1, :].flatten())[0]
        different_neighbors = neighbors[
            np.where(self.districts[neighbors] != self.districts[choice1])[0]
        ]

        # Assuming there is a neighbor in a different district, find one to donate to
        if len(different_neighbors) > 0:
            choice2 = int(np.random.choice(different_neighbors, size=1))

            # Donate the district - if it doesn't disconnect or destroy the other district
            districts1 = np.where(self.districts == self.districts[choice1])[0]

            # TODO: This won't work if one county is, by itself, bigger than the next-biggest district
            # Need to sort out that edge case.
            if len(districts1) > 1:
                new_districts1 = np.delete(
                    districts1, np.where(districts1 == choice1)[0]
                )
                adj1 = self.adj_matrix[new_districts1][:, new_districts1]
                if nx.is_connected(nx.Graph(adj1)):
                    self.districts[choice1] = self.districts[choice2]

    def create_districts(self):
        attempts = 0

        while attempts < self.n_attempts and self.num_districts < 50:
            self.initialize_districts()
            results = self.evaluate_districts()
            # self.recom_step()

            for i in range(self.n_iterations):
                print(i)
                _ = self.smart_assign()
                results = self.evaluate_districts()
                if self.impossible:
                    # Failure
                    raise Exception(
                        "Impossible parameter set... perhaps try more districts"
                    )
                    attempts = 0
                    self.num_districts += 1
                    break
                if (
                    np.max(results) - np.min(results)
                ) / self.ideal_district_size < self.tolerance:
                    # Success
                    attempts = self.n_attempts
                    self.final_districts = self.districts
                    self.final_num_districts = self.num_districts
                    break

            if not hasattr(self, "final_districts"):
                print("failed to find successful districts")

            attempts += 1
        result = self.evaluate_districts(full_output=True)

        if hasattr(self, "final_districts"):
            self.df["district"] = np.array(self.final_districts, dtype="int")
        else:
            self.df["district"] = np.array(self.districts, dtype="int")

        pops = np.zeros((self.n))
        reps = np.zeros((self.n))
        pops_per_rep = np.zeros((self.n))
        for i in range(self.n):
            pops[i] = result[int(self.df["district"].iloc[i]) - 1, 0]
            reps[i] = result[int(self.df["district"].iloc[i]) - 1, 1]
            pops_per_rep[i] = result[int(self.df["district"].iloc[i]) - 1, 2]

        self.df["district_pop"] = pops
        self.df["district_reps"] = reps
        self.df["district_pop_per_rep"] = [f"{x:.2f}" for x in pops_per_rep]

    def evaluate_districts(self, full_output=False, final=False):
        if not final:
            districts = self.districts
            num_districts = self.num_districts
        else:
            districts = self.final_districts
            num_districts = self.final_num_districts

        metric_df = pd.DataFrame(
            np.concatenate(
                [self.metric.reshape(-1, 1), districts.reshape(-1, 1)], axis=1
            ),
            columns=["metric", "districts"],
        )

        pops = metric_df.groupby("districts").sum(numeric_only=True)["metric"].values

        # Allocate minimum reps to each district
        reps = np.array(self.min_reps + np.zeros((num_districts)), dtype="int")
        remaining_reps = self.n_representatives - np.sum(reps)

        # Allocate remaining reps as best we can
        for i in range(remaining_reps):
            # Identify the district with the most underrepresented people, give them another representative
            # As long as there aren't more than max_reps representatives

            sorted_representation = np.argsort(reps / pops)
            j = 0
            while reps[sorted_representation[j]] >= self.max_reps:
                j += 1
                if j > num_districts - 1:
                    j -= 1
                    self.impossible = True
                    break

            reps[sorted_representation[j]] += 1

        # Store evaluation data
        for i, node in enumerate(self.graph.nodes):
            self.graph.nodes[node]["district"] = int(self.districts[i])

        self.reps = reps
        self.pops = pops

        if full_output:
            self.df["district"] = districts
            dem = self.df.groupby("district").sum(numeric_only=True)["DEM"]
            gop = self.df.groupby("district").sum(numeric_only=True)["GOP"]
            # compute dem and gop leanings of each district
            dem = round(reps * dem / (dem + gop))
            gop = reps - dem
            return np.concatenate(
                [
                    pops.reshape(-1, 1),
                    reps.reshape(-1, 1),
                    pops.reshape(-1, 1) / reps.reshape(-1, 1),
                    dem.values.reshape(-1, 1),
                    gop.values.reshape(-1, 1),
                ],
                axis=1,
            )
        else:
            return pops / reps


def generate_choropleth(state, min_reps, n_representatives, num_districts, tolerance):
    """
    Generate a county-level choropleth map for the selected state.
    """
    # Run the districting algorithm
    #

    state_fips = state_fips_map[state]
    counties = alt.topo_feature(data.us_10m.url, "counties")

    districter = Districter(
        state,
        num_districts,
        tolerance,
        min_reps,
        n_representatives,
        column="population",
    )

    districter.create_districts()
    output_df = pd.DataFrame(
        districter.df[
            [
                "FIPS",
                "district",
                "district_pop",
                "district_reps",
                "district_pop_per_rep",
                "County",
            ]
        ]
    )

    chart = (
        alt.Chart(counties)
        .mark_geoshape()
        .encode(
            color="district:N",
            tooltip=[
                alt.Tooltip("County:N", title="County name"),
                alt.Tooltip("district:N", title="District"),
                alt.Tooltip("district_pop:Q", title="Population"),
                alt.Tooltip("district_reps:Q", title="Representatives"),
                alt.Tooltip(
                    "district_pop_per_rep:N", title="Population per representative"
                ),
            ],
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(
                output_df,
                "FIPS",
                [
                    "County",
                    "district",
                    "district_pop",
                    "district_reps",
                    "district_pop_per_rep",
                ],
            ),
        )
        .transform_filter(f"floor(datum.id / 1000) == {state_fips}")
        .project(type="albersUsa")
        .properties(
            width=500,
            height="container",
        )
        .configure_view(
            stroke=None  # Removes borders around the map for cleaner look
        )
    )
    table_json = output_df.to_json(orient="records")
    if hasattr(districter, "final_districts"):
        title = f"{state} - Districting Map"
    else:
        title = f"Districting failed."

    result = {"chart": chart.to_json(), "table": table_json, "title": title}

    return json.dumps(result)
    # return chart.to_json()
