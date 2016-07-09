//Maya ASCII 2016ff07 scene
//Name: rotationDriver_joints.ma
//Last modified: Sat, Jul 09, 2016 11:17:31 PM
//Codeset: 932
requires maya "2016ff07";
requires -nodeType "decomposeRotate" -nodeType "composeRotate" "rotationDriver.py" "1.0.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 7 Enterprise Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode joint -n "src";
	rename -uid "83096AA6-4734-69E6-215F-53A03F6D649E";
	setAttr ".dla" yes;
createNode joint -n "srcEnd" -p "src";
	rename -uid "62C24565-4381-F719-8438-F1BC13A15898";
	setAttr ".t" -type "double3" 5 0 0 ;
createNode joint -n "dst";
	rename -uid "44C2F43E-4985-4BD0-B7CE-8E9B7A25C2D3";
	setAttr ".t" -type "double3" 0 0 2 ;
	setAttr ".dla" yes;
	setAttr ".jo" -type "double3" 0 0 -90 ;
createNode joint -n "dstEnd" -p "dst";
	rename -uid "98346BC5-41A7-076A-FD8E-24883A0E8CCF";
	setAttr ".t" -type "double3" 0 5 0 ;
createNode composeRotate -n "composeRotate1";
	rename -uid "AD4BEF9C-424D-D468-52F7-7384C9C4F4C5";
	setAttr ".ao" -type "double3" 0 0 90 ;
createNode decomposeRotate -n "decomposeRotate1";
	rename -uid "648AB939-452F-90BD-E3B4-10B273AD8068";
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cme" no;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "src.s" "srcEnd.is";
connectAttr "composeRotate1.orx" "dst.rx";
connectAttr "composeRotate1.ory" "dst.ry";
connectAttr "composeRotate1.orz" "dst.rz";
connectAttr "dst.s" "dstEnd.is";
connectAttr "dst.ro" "composeRotate1.ro";
connectAttr "decomposeRotate1.orl" "composeRotate1.rl";
connectAttr "decomposeRotate1.obh" "composeRotate1.bh";
connectAttr "decomposeRotate1.obv" "composeRotate1.bv";
connectAttr "src.r" "decomposeRotate1.r";
connectAttr "src.ro" "decomposeRotate1.ro";
// End of rotationDriver_joints.ma
