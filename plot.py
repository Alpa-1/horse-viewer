import plotly.graph_objects as go

# Values for each attribute, represented as (starting point, length)
values = {
    "START": {
        "MIN": (365.39392, 42.050568),
        "MED": (407.44449, 27.093872),
        "MAX": (434.53836, 45.368195),
    },
    "SPEED": {
        "MIN": (381.24475, 27.305603),
        "MED": (408.55035, 20.274323),
        "MAX": (428.82468, 23.988007),
    },
    "STAMINA": {
        "MIN": (382.35062, 26.199738),
        "MED": (408.55035, 13.4548035),
        "MAX": (422.00516, 25.093842),
    },
    "FINISH": {
        "MIN": (365.39392, 25.093872),
        "MED": (390.48779, 20.274323),
        "MAX": (410.76212, 25.093872),
    },
    "HEART": {
        "MIN": (377.7428, 35.231033),
        "MED": (412.97382, 24.882141),
        "MAX": (437.85596, 34.125153),
    },
    "TEMPER": {
        "MIN": (320.23746, 36.336914),
        "MED": (356.57437, 25.988007),
        "MAX": (382.56238, 34.125153),
    },
}

# Vibrant rank colors with gradients
rank_colors = {
    "D-": "#ff6666",
    "D": "#ff3333",
    "D+": "#cc0000",
    "C-": "#99ccff",
    "C": "#66b2ff",
    "C+": "#3399ff",
    "B-": "#ffcc99",
    "B": "#ff9966",
    "B+": "#ff6600",
    "A-": "#99ff99",
    "A": "#66ff66",
    "A+": "#33cc33",
    "S-": "#cc99ff",
    "S": "#b266ff",
    "S+": "#9933ff",
    "SS-": "#9966cc",
    "SS": "#663399",
    "SS+": "#330066",
    "SSS-": "#663366",
    "SSS": "#4d004d",
    "SSS+": "#330033",
}

# Legend ranks and ranges
rank_legend = {
    "D-": (125.99999308333334, 146.47618369444444),
    "D": (146.47618369444444, 166.95237430555557),
    "D+": (166.95237430555557, 187.42855408333335),
    "C-": (187.42855408333335, 207.90474469444447),
    "C": (207.90474469444447, 228.38093530555557),
    "C+": (228.38093530555557, 248.85712408333333),
    "B-": (248.85712408333333, 269.3333146944444),
    "B": (269.3333146944444, 289.80950530555555),
    "B+": (289.80950530555555, 310.28571408333335),
    "A-": (310.28571408333335, 330.76190469444447),
    "A": (330.76190469444447, 351.2380953055556),
    "A+": (351.2380953055556, 371.71430408333333),
    "S-": (371.71430408333333, 392.19049469444445),
    "S": (392.19049469444445, 412.6666853055556),
    "S+": (412.6666853055556, 433.14286408333334),
    "SS-": (433.14286408333334, 453.61905469444446),
    "SS": (453.61905469444446, 474.0952453055556),
    "SS+": (474.0952453055556, 494.57142408333334),
    "SSS-": (494.57142408333334, 515.0476146944444),
    "SSS": (515.0476146944444, 535.5238053055556),
    "SSS+": (535.5238053055556, 555.9999959166666),
}


# Function to determine the rank category for a given value
def determine_rank_category(value, rank_legend):
    for rank, (low, high) in rank_legend.items():
        if low <= value < high:
            return rank
    return "SSS+"  # If it exceeds the highest range


# Prepare data for the interactive plot
traces = []
segment_types = ["MIN", "MED", "MAX"]
offsets = {"MIN": -0.2, "MED": 0, "MAX": 0.2}

for segment_type in segment_types:
    segment_starts = []
    segment_lengths = []
    segment_colors = []
    for attribute, measurements in values.items():
        start, length = measurements[segment_type]
        segment_starts.append(start)
        segment_lengths.append(length)
        # Determine the rank color for each segment
        current_value = start
        while length > 0:
            current_rank_index = next(
                index
                for index, (low, high) in enumerate(rank_legend.values())
                if low <= current_value < high
            )
            current_rank = list(rank_legend.keys())[current_rank_index]
            low, high = rank_legend[current_rank]
            segment_colors.append(rank_colors[current_rank])
            length_in_rank = min(high - current_value, length)
            current_value += length_in_rank
            length -= length_in_rank

    traces.append(
        go.Bar(
            x=list(values.keys()),
            y=segment_lengths,
            base=segment_starts,
            name=segment_type,
            marker_color=segment_colors,
            offset=offsets[segment_type],
            width=0.2,
        )
    )

# Create the interactive plot
fig = go.Figure(data=traces)
fig.update_layout(
    title="Interactive Rank Distribution of MIN, MED, and MAX Segments",
    xaxis_title="Attributes",
    yaxis_title="Value",
    barmode="group",
    legend_title="Segments",
)

# Show the plot
fig.show()
