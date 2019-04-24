# Changes from v2 to v3

* `type` has been renamed to `crp_type` and its specification changed...
* If `crp_type` is not set then the challenge is static (no containers or VMs).
* Supported `crp_type` values: `docker` same as before, `gce` for new VM based challenges on GCE.
* `crp_config` is different for container vs VM based providers.
* `crp_config.<container>.mem_limit` has been converted to `crp_config.<container>.mem_limit_mb`.
* All metadata fields and files will be handled by the new platform instead.
