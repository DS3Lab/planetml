# Job Types

## Interactive Jobs

* The instruction queue should be taken care, i.e., if a job is put into the instructions list, we should check if it is consumed by the worker in a certain amount of time. If now, we should fallback to batch job.
* 