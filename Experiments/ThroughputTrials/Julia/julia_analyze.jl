# let's open one pcap and get a single plot going

# using Pkg;
# Pkg.add("DataFrames")
# Pkg.add("CSV")
# Pkg.add("Query")
using DataFrames
using CSV
using Query
using Dates

fname = "../data/2020-07-27/mlcnetA.cs.wpi.edu_cubic_0/local.csv"

df = DataFrame(CSV.File(fname))

function summarize_trial(df, start_bytes=0, end_bytes = 1e9)
    x = "tcp.seq"
    df |> @filter(x -> 
                     x[Symbol("tcp.seq")] > start_bytes && 
                     x[Symbol("tcp.seq")] < end_bytes ) |> DataFrame
end


df |> @filter ()


Dates.DateTime(df["frame.time_epoch"][1] / 1000)