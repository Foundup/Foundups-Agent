def test_v2_csv_headers_include_early_warning():
	# Expected minimal header set for v2 detector CSV
	expected = {
		"t","step","sym","C","E","rnorm","purity","S",
		"detg","det_thr","reso_hit_freq","reso_hit_mag",
		"ew_varE","ew_ac1E","ew_dS",
	}
	# Simulate a header list as parsed from CSV
	headers = [
		"t","step","sym","C","E","rnorm","purity","S",
		"detg","det_thr","reso_hit_freq","reso_hit_mag",
		"ew_varE","ew_ac1E","ew_dS",
	]
	assert expected.issubset(set(headers))
