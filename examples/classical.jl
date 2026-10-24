module ClassicalControl
using Random, Statistics, DelimitedFiles, TOML, SHA

module Kernel
using Random
# Load definitions without the archive's unused third-party imports.
Base.include(expr -> expr isa Expr && expr.head == :function ? expr : nothing,
             @__MODULE__, joinpath(@__DIR__, "..", "Classical Noise Code"))
end

function trajectory(; L::Integer=16, p::Real=0.5, psq::Real=0.01,
                      ptq::Real=0.001, steps::Integer=2L^2, seed::Integer=2026)
    2 <= L <= 256 || throw(ArgumentError("L must be from 2 to 256"))
    all(x -> isfinite(x) && 0 <= x <= 1, (p, psq, ptq)) || throw(ArgumentError("probabilities must be in [0,1]"))
    1 <= steps <= 2L^2 || throw(ArgumentError("steps must be from 1 to 2L^2"))
    0 <= seed <= typemax(Int32) || throw(ArgumentError("seed must be a nonnegative 32-bit integer"))
    Random.seed!(seed)
    Kernel.L, Kernel.vector, Kernel.psq, Kernel.ptq = L, collect(1:L), psq, ptq
    bits = rand(0:1, L)
    trace = zeros(steps + 1)
    trace[1] = 1 - 2mean(bits)
    for t in 1:steps
        rand() < p ? Kernel.control_map(bits) : Kernel.chu_map(bits)
        trace[t + 1] = 1 - 2mean(bits)
    end
    (; magnetization=trace, bits=copy(bits))
end

function run(output_path)
    output = abspath(output_path)
    ispath(output) && throw(ArgumentError("output already exists: $output"))
    sizes, probabilities, noise, samples, seed = [8, 16, 32], collect(0.0:0.1:1.0), [0.01, 0.3], 64, 2026
    mkpath(dirname(output))
    stage = mktempdir(dirname(output))
    try
        rows = Any[]
        for (ni, psq) in enumerate(noise), L in sizes, (pi, p) in enumerate(probabilities)
            values = [trajectory(; L, p, psq, ptq=psq/10, seed=seed+100000ni+1000L+100pi+i).magnetization[end]
                      for i in 1:samples]
            push!(rows, (L, p, psq, psq/10, samples, mean(values), std(values)/sqrt(samples)))
        end
        open(joinpath(stage, "magnetization.csv"), "w") do io
            println(io, "L,p,psq,ptq,trajectories,mean_mz,se_mz")
            for row in rows
                println(io, join(row, ','))
            end
        end
        open(joinpath(stage, "metadata.toml"), "w") do io
            TOML.print(io, Dict("seed"=>seed, "sizes"=>sizes, "probabilities"=>probabilities,
                "psq"=>noise, "ptq_rule"=>"psq/10", "trajectories"=>samples,
                "steps"=>"2*L^2", "seed_rule"=>"seed+100000*noise_index+1000*L+100*p_index+trajectory",
                "julia_version"=>string(VERSION),
                "source_sha256"=>bytes2hex(sha256(read(joinpath(@__DIR__, "..", "Classical Noise Code"))))))
        end
        mv(stage, output)
    finally
        isdir(stage) && rm(stage; recursive=true)
    end
    println("Saved classical magnetization sweep to $output")
end
end

if abspath(PROGRAM_FILE) == (@__FILE__)
    length(ARGS) == 1 || error("usage: julia --project=. examples/classical.jl OUTPUT_DIRECTORY")
    ClassicalControl.run(ARGS[1])
end
