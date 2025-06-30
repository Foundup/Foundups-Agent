# WSP-54: ScoringAgent Module

This module contains the `ScoringAgent`, responsible for providing objective metrics for code complexity and importance.

## Core Mandate

To provide objective metrics for code complexity and importance.

## Trigger

Dispatched on-demand by the WRE.

## Duties

1.  **Analyze Code:** Analyze a module's code and documentation.
2.  **Calculate Scores:** Calculate and assign "MPS + LLME" scores based on factors like code length, cyclomatic complexity, documentation quality, and dependencies.

## Output

A scoring report for the specified module. 