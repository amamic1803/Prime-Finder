use malachite::num::arithmetic::traits::FloorSqrt;
use malachite::Natural;
use pyo3::prelude::*;

#[pyfunction]
fn is_prime(n: Natural) -> bool {
    //! Check if a number is prime.

    if n <= Natural::const_from(3) {
        return n > Natural::const_from(1);
    }

    if &n % Natural::const_from(2) == Natural::const_from(0) || &n % Natural::const_from(3) == Natural::const_from(0) {
        return false;
    }

    let limit = (&n).floor_sqrt();
    let mut i = Natural::const_from(5);
    while i <= limit {
        if &n % &i == Natural::const_from(0) || &n % (&i + Natural::const_from(2)) == Natural::const_from(0) {
            return false;
        }
        i += Natural::const_from(6);
    }

    true
}

#[pyfunction]
fn sieve_of_eratosthenes(n: u64) -> Vec<u64> {
    //! Generate all prime numbers up to a given number using the sieve of Eratosthenes.
    
    match n {
        0..=1 => Vec::with_capacity(0),
        2 => vec![2],
        _ => {
            let mut results = vec![2];
            let mut sieve = vec![true; (n - 1) as usize / 2];

            let ind_to_val = |i: usize| ((i as u64) << 1) + 3; // calculate number value from index in sieve
            let val_to_ind = |v: u64| ((v - 3) >> 1) as usize; // calculate index in sieve from number value

            for prime_ind in 0..sieve.len() {
                if sieve[prime_ind] {
                    // get prime number value
                    let prime_val = ind_to_val(prime_ind);

                    // check all multiples of prime number value and mark them as not prime
                    // start checking at prime_val^2 (all smaller multiples have already been checked by smaller primes)
                    let mut check_val = prime_val * prime_val;
                    let mut check_ind = val_to_ind(check_val);
                    if check_ind >= sieve.len() {
                        break;
                    }

                    while check_ind < sieve.len() {
                        sieve[check_ind] = false;
                        // we want check_val to always be odd, prime_val is always odd so we can just add prime_val * 2
                        // (because if we added 2 odd numbers we would get an even number)
                        check_val += prime_val << 1;
                        check_ind = val_to_ind(check_val);
                    }
                }
            }

            // convert sieve indices that are true to their corresponding number values and add them to results
            results.extend(sieve.into_iter().enumerate().filter_map(|(i, prime)| if prime { Some(ind_to_val(i)) } else { None }));

            // return results
            results
        }
    }
}

#[pymodule]
fn primes(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_prime, m)?)?;
    m.add_function(wrap_pyfunction!(sieve_of_eratosthenes, m)?)?;
    Ok(())
}
