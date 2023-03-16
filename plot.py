import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def y_func(x, p):
    """ """
    return 1 - (1 - (1 / p)) ** x


def plot_probability(trials, probability, file_name):
    """ """
    # plot up to 5 times the drop rate
    x = range(1, probability * 5)
    y = [y_func(i, probability) for i in x]

    fig, ax = plt.subplots()
    ax.plot(x, y)

    ax.plot(
        [trials, trials],
        [y_func(trials, probability), ax.get_ylim()[0]],
        linestyle="--",
        color="gray",
    )
    ax.plot(
        [0, trials],
        [y_func(trials, probability), y_func(trials, probability)],
        linestyle="--",
        color="gray",
    )

    ax.set_xlabel("Number of Kills")
    ax.set_ylabel("Percent Chance of Receiving The Drop")
    ax.set_title(
        f"Percent Chance of Receiving The Drop After {trials} KC (P=1/{probability})"
    )
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.set_xlim(0)
    ax.set_ylim(0)
    ax.annotate(
        f"{y_func(trials, probability)*100:.0f}%",
        xy=(0, y_func(trials, probability)),
        xycoords="data",
        color="r",
        fontsize=9,
    )
    # Show the plot
    plt.savefig(file_name)
