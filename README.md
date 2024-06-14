# XCT-Explorer
interactive GUI to plan CT experiments

The XCT-Explorer is a graphic user interface designed to be an intuitive and interactive tool to help planning CT experiments according to a step-by-step protocol. This should allow for an interactive balancing of the various scanning parametes and for a first assessment of the feasibility of experiments. Details about the protocol and the equations that link the various parameters can be found in (under review). A simplified protocol is described bellow:
Important: For simplicity, some advanced options are not considered. Therefore, always use interpret the results critically and discuss your assessment with a CT expert.
Step 1: Define the Resolution controlling parameters
-	Click the Geometric Parameters tab.
-	Select the purpose of the study
-	Adjust the Sample Diameter slider
-	If “Minimum Feature Size” is larger than your expectation consider 
	Choose the Full Camera 
	Decrease the Binning 
	Decrease the Sample Diameter. 
-	Different combinations of binning and detector size may give the same voxel size. In this case choose the combination with higher binning as that reduces the scan time and the data size.
Note 1: The equations linking the various parameters in the resolution tab is only valid for a specific scanner configuration (CoreTom from Tescan with detector size 2856x2856).
Step 2: Define the Composition of the sample
-	Click the Composition Parameters tab
-	Select up to 4 of the most relevant Phases in the sample
-	Input the approximate Volume Fraction for each phase. The sum of all phases should be 1 minus the volume fraction of the porosity
-	The best contrast between phases is achieved using a range of energies that maximizes the distance between the attenuation curves (see plot). Matching curves imply that the phases cannot be distinguished with CT. 
Note 2: the composition tab uses a database of phases adjusted from Hanna and Ketcham 2017 (10.1016/j.chemer.2017.01.006). In future versions it will be possible to add new phases to the database. 
Note 3: If more than four phases are present or if some phases are not interesting to the scientific question, they can be grouped into classes with similar attenuation. If a component within a voxel is not pure, e.g. aqueous solution containing iodine or samples with grains or pores with sizes close to the voxel size, it counts as one phase. The attenuation coefficients of the mixture of phases can be calculated using the NIST database and add to the GUI database. 
Step 3: Tune the X-ray spectra
-	Choose a filter option
-	Adjust the Maximum Energy slider 
	If contrast is not a problem aim at 160 kV 
	The yellow curve should be at least 10% at Emax. If not reduce “Sample Diameter” 
Step 4: Confirm the Time
-	Input the Number of scans on the sidebar if more than 1 sample or multiple scans per sample (e.g. if the sample height is higher than the diameter).
-	If “Experiment Time” is red, consider reducing the scanning time for images with higher quality
-	Check if the “Experiment Time” is realistic for your possibilities
-	To reduce the scanning time consider the following strategies:
	reduce Diameter and/or reduce Filter 
	Increase the Maximum Energy
	increase the voxel size by increasing Binning or decreasing Camera Size
Note 4: Consider the Experiment Time just a rough approximation
