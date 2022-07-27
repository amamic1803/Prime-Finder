use num_integer::sqrt;
use pyo3::prelude::*;

#[pyfunction]
fn check_if_prime_u128(n: u128) -> bool {
    if n < 2 {
        return false;
    } else if n == 2 {
        return true;
    } else {
        if n % 2 == 0 {
            return false;
        }
        for i in (3..=sqrt(n)).step_by(2) {
            if n % i == 0 {
                return false;
            }
        }
        return true
    }
}

#[pymodule]
fn rust(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(check_if_prime_u128, m)?)?;
    Ok(())
}
