import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.spatial.distance import cdist, mahalanobis
from scipy.stats import chi2, hmean, norm
from scipy.stats import multivariate_normal as mvn


def covariance_matrix(correlation_coefficient, std_A, std_B):
    off_diagonal_term = correlation_coefficient * (std_A * std_B)
    c = np.array([[std_A**2, off_diagonal_term], [off_diagonal_term, std_B**2]])
    return c


fig = plt.figure(figsize=[10, 5])
N = 1000
A_mean = 0
A_std = 1
B_mean = 0
B_std = 1
outlier_point1 = [3.0, 3.0]
outlier_point2 = [1.5, -1.5]
A = A_std * np.random.randn(N) + A_mean
B = B_std * np.random.randn(N) + B_mean
plt.subplot(121)
plt.scatter(A, B, alpha=0.25, c="#82aaff")
plt.scatter(outlier_point1[0], outlier_point1[1], c="salmon")
plt.scatter(outlier_point2[0], outlier_point2[1], c="goldenrod")
plt.xlabel("A")
plt.ylabel("B")
plt.title("Uncorrelated data")
plt.subplot(122)
c = covariance_matrix(correlation_coefficient=0.95, std_A=A_std * 2, std_B=B_std * 2)
mu = np.array([A_mean, B_mean])
correlated_results = mvn.rvs(size=N, mean=mu, cov=c)
plt.scatter(correlated_results[:, 0], correlated_results[:, 1], alpha=0.25)
plt.scatter(outlier_point1[0], outlier_point1[1], c="salmon")
plt.scatter(outlier_point2[0], outlier_point2[1], c="goldenrod")
plt.xlabel("A")
plt.ylabel("B")
plt.title("Correlated data")
plt.tight_layout()
plt.savefig("correlations_2d.png", bbox_inches="tight")
plt.show()

x = np.concat([A.reshape(-1, 1), B.reshape(-1, 1)], axis=1)
distances = cdist(x, np.zeros((1, 2))) ** 2
x_arr = np.linspace(0, 20, 100)
plt.plot(x_arr, chi2.pdf(x_arr, df=2))
plt.hist(distances, density=True, bins=100)
plt.show()


D = 20
c_high_dim = np.eye(D) * 0.1 + np.zeros((D, D)) + 0.9
mu = np.zeros((D))
corr_high_dim = mvn.rvs(size=N, mean=mu, cov=c_high_dim)

VI = np.linalg.inv(c_high_dim)
x_test = np.zeros((D)) + 5
test_distance = mahalanobis(x_test, mu, VI)
print("test distance = ", test_distance)
print(norm.isf(chi2.sf(test_distance**2, df=D)))

fig = plt.figure(figsize=[8, 8])
plt.scatter(
    corr_high_dim[:, 0],
    corr_high_dim[:, 1],
    alpha=0.25,
    label="Sampled points",
    c="tab:blue",
)
plt.scatter(x_test[0], x_test[1], c="goldenrod", label="$x_{test}$")
plt.xlabel("Dimension 0")
plt.ylabel("Dimension 1")
plt.legend()
plt.tight_layout()
plt.show()

distances = np.array([mahalanobis(xi, mu, VI) for xi in corr_high_dim]) ** 2
x_arr = np.linspace(0, 50, 100)
plt.hist(distances, density=True, bins=100, label="Sampled points")
plt.plot(x_arr, chi2.pdf(x_arr, df=D), lw=2.0, label="$\chi^2$, 20 d.o.f.")
plt.axvline(test_distance**2, c="goldenrod", label="$x_{test}$")
plt.xlabel("Squared distance")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.show()


# Parameters

num_points = 500
radius = 1.0
bgcolor = "#232136"
# Random points on the sphere
phi = np.random.uniform(0, 2 * np.pi, num_points)
costheta = np.random.uniform(-1, 1, num_points)
theta = np.arccos(costheta)
x = radius * np.sin(theta) * np.cos(phi)
y = radius * np.sin(theta) * np.sin(phi)
z = radius * costheta
# Center point
x_center, y_center, z_center = [0], [0], [0]
# Blue sphere points
sphere_trace = go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode="markers",
    marker=dict(size=3, color="#82aaff"),
    hoverinfo="none",
    showlegend=False,
)
# Yellow center point
center_trace = go.Scatter3d(
    x=x_center,
    y=y_center,
    z=z_center,
    mode="markers",
    marker=dict(size=5, color="goldenrod"),
    hoverinfo="none",
    showlegend=False,
)
# Layout configuration
layout = go.Layout(
    scene=dict(
        xaxis=dict(showbackground=False, showticklabels=False, title="", visible=False),
        yaxis=dict(showbackground=False, showticklabels=False, title="", visible=False),
        zaxis=dict(showbackground=False, showticklabels=False, title="", visible=False),
        bgcolor=bgcolor,
    ),
    paper_bgcolor=bgcolor,
    plot_bgcolor=bgcolor,
    margin=dict(l=0, r=0, b=0, t=0),
    hovermode=False,
)
fig = go.Figure(data=[sphere_trace, center_trace], layout=layout)
html_plot = fig.to_html(
    include_plotlyjs="cdn",
    full_html=False,
    post_script=None,
    config={"displayModeBar": False},
    auto_open=False,
    include_mathjax=False,
    div_id=None,
)

with open(
    "/Users/christian/projects/christian-johnson.github.io/assets/html/mahalanobis/sphere_plot.html"
) as f:
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #1f1d2e;
            }}
        </style>
    </head>
    <body>
        {html_plot}
    </body>
    </html>
    """
    f.write(html_plot)


def marginal_distribution(i, j, mu, c):
    """
    The marginal distributions of the mean, covariance, and shape of a
    skew-normal distribution, in 2 dimensions (projected down from N dimensions)

    We need these for evaluating the pairwise distances to find the distance
    to any given snapshot

    From Azzalini (1999)
    """
    mu_ = mu[[i, j]]
    omega11 = c[[i, j]][:, [i, j]]
    return mu_, omega11


def high_dim_mahalanobis_z_score(x: np.array, mu: np.array, c: np.array) -> np.float32:
    p = c.shape[0]
    triu_indices = np.triu_indices(p, k=1)
    distances = np.zeros((p, p))
    for idx in range(len(triu_indices[0])):
        i = triu_indices[0][idx]
        j = triu_indices[1][idx]

        mu_ = mu[[i, j]]
        c_ = c[[i, j]][:, [i, j]]

        distances[triu_indices[0][i], triu_indices[1][i]] = (
            mahalanobis(
                x[[i, j]],
                mu_,
                np.linalg.inv(c_),
            )
            ** 2
        )
    z = norm.isf(
        hmean(
            chi2.sf(
                distances[triu_indices],
                df=2,
            ),
        )
    )
    return z


def high_dim_mahalanobis_z_score(x: np.ndarray, mu: np.ndarray, c: np.ndarray) -> float:
    """
    Compute a combined z-score based on the harmonic mean of Mahalanobis distance
    p-values across all 2D projections of a high-dimensional point.

    Parameters
    ----------
    x : np.ndarray, shape (p,)
        The p-dimensional data point.
    mu : np.ndarray, shape (p,)
        The p-dimensional mean vector.
    c : np.ndarray, shape (p, p)
        The p x p covariance matrix.

    Returns
    -------
    z_score : float
        The z-score corresponding to the harmonic mean of the chi-squared p-values
        from the 2D Mahalanobis distances.

    Example
    -------
    >>> z = high_dim_mahalanobis_z_score(x, mu, c)

    Notes
    -----
    This function computes Mahalanobis distances in each unique 2D subspace defined
    by all pairs of dimensions (i < j), and then aggregates the resulting
    chi-squared p-values (with df=2) using the harmonic mean before converting
    to a z-score using the standard normal inverse survival function.
    """
    # Shape assertions
    assert x.ndim == 1 and mu.ndim == 1, "x and mu must be 1D arrays"
    assert c.ndim == 2 and c.shape[0] == c.shape[1], "c must be a square matrix"
    p = x.shape[0]
    assert mu.shape[0] == p and c.shape == (p, p), (
        "x, mu, and c must have consistent dimensions"
    )

    triu_i, triu_j = np.triu_indices(p, k=1)
    dists_squared = np.empty(triu_i.shape[0])

    for idx, (i, j) in enumerate(zip(triu_i, triu_j)):
        x_ij = x[[i, j]]
        mu_ij = mu[[i, j]]
        c_ij = c[[i, j]][:, [i, j]]
        dists_squared[idx] = mahalanobis(x_ij, mu_ij, np.linalg.inv(c_ij)) ** 2

    # Convert squared distances to p-values under chi-squared distribution with 2 DOF
    p_values = chi2.sf(dists_squared, df=2)

    # Combine p-values using harmonic mean and return corresponding z-score
    z_score = norm.isf(hmean(p_values))
    return z_score


high_dim_mahalanobis_z_score(x_test, np.zeros((D)), c_high_dim)
