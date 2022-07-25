use primes::is_prime;
use pyo3::prelude::*;


#[pyfunction]
fn run(n: u64) -> PyResult<bool> {
    Ok(is_prime(n))
}

#[pymodule]
fn rust_check_if_prime(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run, m)?)?;
    Ok(())
}