# CAL RC5A Supervisor Apparatus

Status: research supervisor material. This directory is forbidden to a fresh RC5A implementer before implementation/test freeze.

## Purpose

Qualify a successor evaluator that separates:

- normative security-class conformance; and
- diagnostic preservation properties.

The evaluator deliberately does not compare exact diagnostic strings across implementations.

## Frozen predecessor

RC5 terminal branch:
`research/cal-rc5-independent-asymmetric-two-receipt-post-reveal-20260905`

Terminal commit:
`abfbf9992577072a6a6417a9584bf07120e12142`

Disposition:
`INCONCLUSIVE_EVALUATOR_INVALID`

RC5A must not be used to relabel RC5.

## Current supervisor apparatus

- hidden cases: `23`
- reference local normative matches: `23/23`
- seeded weak controls caught: `6/6`
- local qualification: `PASS`
- seal status: `NOT_SEALED_PENDING_INDEPENDENT_ORACLE_REVIEW`

The local reference pass is apparatus development evidence only. It is not independent oracle qualification and is not a scientific result about fresh recoverability.

## Before seal

A separate reviewer must review the hidden expected normative classes and diagnostic metamorphic relations against the public RC5A spec without seeing candidate outputs. Material disagreement blocks seal.

No fresh RC5A implementation should exist before evaluator qualification/seal if the final experiment is intended to test fresh recoverability.
