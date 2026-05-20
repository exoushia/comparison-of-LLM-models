**Input:** Load (PLₕ), Shifted load (kⁱ), Elastic loads (spₕᵃ), User preference (uppₕᵃ), Contract limit, ς

**Output:** Desirable user preference parameter threshold such that f(αₕᵃ) ≤β

**Begin** 1: **Initialize** αₕᵃ=0, app=0, β=A such that kⁱ =[kⁱ]^T, ∀i ∈I
    2: **for** h=1,2,...,H **do**
    3: **if** (PL > 250) **then**
    4: **for** a=1,2,...,A **do**
    5: **if** spₕᵃ > 0 and spₕᵃ = kⁱ **then**
    6: αₕᵃ = spₕᵃ and app=app+1
    7: **if** app > β break **end if**   **end if**   **end for**   **end if**   **end for**
    8: **initialize** i=0, ς=3000, kⁱ=0
    9: **for** h=1,2,...,H **do**
    10: **if** (h=off-peak/normal) **then**
    11: update PLₕ=PLₕ^+ + αₕᵃ   **end if**   **end for**   End