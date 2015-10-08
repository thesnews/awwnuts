Simple scanner that checks for the existence of our generator tag
and a few other things.

It's slow and clunky, and it only scans one level beyond the root,
but it does the job.

It doesn't rate limit, so don't be a jerk. Only use this on your
resources.

Install:
`pip --user -r requirements.txt`

Run:
`python awwnuts.py http://path/to/site`
