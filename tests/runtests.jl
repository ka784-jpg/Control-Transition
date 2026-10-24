using Test, Random, Statistics
include("../examples/classical.jl")
const C = ClassicalControl
const K = C.Kernel

@testset "Classical trajectories" begin
    for L in (2, 8, 16), p in (0.0, 0.5, 1.0)
        result = C.trajectory(; L, p, psq=0.0, ptq=0.0, seed=71)
        @test all(-1 .<= result.magnetization .<= 1)
        @test all(x -> x in (0, 1), result.bits)
        @test result.magnetization == C.trajectory(; L, p, psq=0.0, ptq=0.0, seed=71).magnetization
        p == 1 && @test result.magnetization[end] == 1
    end
end

@testset "Diagonal depolarizing channels" begin
    Random.seed!(2026)
    K.L, K.vector = 4, [1, 2, 3, 4]
    for probability in (0.0, 0.4, 1.0)
        K.psq, K.ptq = probability, probability
        single = mean(K.single_dep([0, 0, 0, 0], 1)[1] for _ in 1:20000)
        @test abs(single - probability/2) < 0.015
        frequencies = zeros(4)
        for _ in 1:20000
            bits = K.two_dep([0, 0, 0, 0], 1)
            frequencies[1 + bits[1] + 2bits[2]] += 1
        end
        @test maximum(abs, frequencies/20000 - [1-3probability/4, probability/4, probability/4, probability/4]) < 0.015
    end
    K.vector = [1, 2, 3, 4]
    K.left_trans()
    @test K.vector == [2, 3, 4, 1]
    K.right_trans()
    @test K.vector == [1, 2, 3, 4]
    @test K.periodic_index(5) == 1
    K.ptq = 0.0
    bits = K.chu_map_loc([0, 0, 0, 0], 4)
    @test bits[2:3] == [0, 0]
end

@testset "Input and output protection" begin
    for kwargs in ((;L=1), (;p=NaN), (;psq=-0.1), (;ptq=1.1), (;steps=0), (;seed=-1))
        @test_throws ArgumentError C.trajectory(;kwargs...)
    end
    mktempdir() do dir
        @test_throws ArgumentError C.run(dir)
    end
end
