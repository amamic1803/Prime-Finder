use malachite::Natural;
use malachite::num::arithmetic::traits::CeilingSqrt;
use num::integer::Roots;
use pyo3::prelude::*;
use std::str::FromStr;

#[pyfunction]
fn is_prime_u128(x: u128) -> bool {
    return if x < 2 {
        false
    } else if x == 2 {
        true
    } else if x % 2 == 0 {
        false
    } else {
        for i in (3..(x.sqrt() + 1)).step_by(2) {
            if x % i == 0 {
                return false
            }
        }
        true
    }
}

#[pyfunction]
fn is_prime_big(x: &str) -> bool {
    let x: Natural = Natural::from_str(x).unwrap();
    let big_0: Natural = Natural::from(0_u8);
    let big_2: Natural = Natural::from(2_u8);
    let big_3: Natural = Natural::from(3_u8);
    let root_x: Natural = x.clone().ceiling_sqrt();
    return if x < big_2 {
        false
    } else if x == big_2 {
        true
    } else if &x % &big_2 == big_0 {
        false
    } else {
        let mut curr_num = big_3;
        while curr_num < root_x {
            if &x % &curr_num == big_0 {
                return false
            }
            curr_num += & big_2;
        }
        true
    }
}

#[pyfunction]
fn sieve_of_atkin(limit: usize) -> Vec<usize> {
    let mut results: Vec<usize> = vec![];

    let limit: u128 = limit as u128;

    if limit > 2 {
        results.push(2);
    }
    if limit > 3 {
        results.push(3);
    }

    let mut sieve: Vec<bool> = vec![];
    for _ in 0..(limit + 1) {
        sieve.push(false);
    }

    let mut x: u128 = 1;
    let mut y: u128;
    let mut n: u128;
    while (x * x) <= (limit as u128) {
        y = 1;
        while (y * y) <= limit {
            n = (4 * x * x) + (y * y);
            if (n <= limit) && ((n % 12 == 1) || (n % 12 == 5)) {
                sieve[n as usize] ^= true;
            }

            n = (3 * x * x) + (y * y);
            if (n <= limit) && (n % 12 == 7) {
                sieve[n as usize] ^= true;
            }

            if x > y {
                n = (3 * x * x) - (y * y);
                if (n <= limit) && (n % 12 == 11) {
                    sieve[n as usize] ^= true;
                }
            }

            y += 1;
        }
        x += 1;
    }

    let mut r: u128 = 5;
    while (r * r) <= limit {
        if sieve[r as usize] {
            for i in (((r * r) as usize)..((limit + 1) as usize)).step_by((r * r) as usize) {
                sieve[i] = false;
            }
        }
        r += 1;
    }

    for a in (5_usize)..((limit + 1) as usize) {
        if sieve[a] {
            results.push(a);
        }
    }

    results
}

#[pymodule]
fn rust(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_prime_u128, m)?)?;
    m.add_function(wrap_pyfunction!(is_prime_big, m)?)?;
    m.add_function(wrap_pyfunction!(sieve_of_atkin, m)?)?;
    Ok(())
}
