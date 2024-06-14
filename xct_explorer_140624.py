#importing all the required packages
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from scipy.optimize import curve_fit
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout='wide',page_title='XCT-Explorer v140624')
tabUploads, tabGeometry, tabComposition =st.tabs(['Instructions',':blue[Geometric Parameters]',':violet[Composition Parameters]'])

############################################ Upload databases ################################################### 
with tabUploads:    # here the data could be loaded either from a disk or URL location, or drag and drop. Currently is using a database uploaded in google sheets. the scanner specific settings could also be loaded 
    st.write('The XCT-Explorer is a graphic user interface designed to be an intuitive and interactive tool to help planning CT experiments according to a step-by-step protocol. This should allow for an interactive balancing of various scanning parametes and for a first assessment of the feasibility of experiments. Details about the protocol and the equations that link the various parameters can be found in (under review). A simplified protocol is described bellow.')
    st.subheader('Important: For simplicity, some advanced options are not considered. Always interpret the results critically and discuss your assessment with a CT expert')
    st.write('**Step 1: Define the Resolution controlling parameters**')
    st.write(' -	Click the :blue[Geometric Parameters] tab')
    st.write('-	Select the purpose of the study')
    st.write('-	Adjust the Sample Diameter slider')
    st.write(' -	If “Minimum Feature Size” is larger than your expectation consider: 1) Increase detector width; 2) Decrease Binning; 3) Decrease Sample Diameter') 
    st.write('**Tip:** Different combinations of binning and detector size may give the same voxel size. In this case choose the combination with higher binning as that reduces the scan time and the data size')
    st.write(' **Step 2: Define the Composition of the sample**')
    st.write('-	Click the :violet[Composition Parameters] tab')
    st.write('-	Select up to 4 of the most relevant Phases in the sample')
    st.write('-	Input the approximate Volume Fraction for each phase')
    st.write('**Step 3: Tune the X-ray spectra**')
    st.write('-	Select a filter option')
    st.write('-	Adjust the Maximum Energy slider')
    st.write('**Tip:** The best contrast between phases is achieved using a range of energies that maximizes the distance between the attenuation curves (see plot)')
    st.write('**Step 4: Confirm the Time**')
    st.write('-	Input the :green[Number of scans] on the sidebar if more than 1 sample or multiple scans per sample')
    st.write('-	If :red[Experiment Time] is red or warning pops out, consider reducing the scanning time to achieve images with higher quality')
    st.write('-	Confirm that the Experiment Time is realistic for your possibilities')
    st.write('**Tip:** to reduce the scanning time consider the following strategies: 1) reduce Diameter; 2) reduce Filter; 3)	increase Maximum Energy; 4) increase Binning, 5) decrease detector width')
    st.write('Note 1: the equations linking the various parameters in the resolution tab is only valid for a specific scanner configuration ( in this version is a CoreTom from Tescan with detector size 2856x2856)')    
    st.write('Note 2: the composition tab uses a database of phases adjusted from Hanna and Ketcham 2017 (10.1016/j.chemer.2017.01.006)')     
    st.write('Note 3: Consider the Experiment Time is just a rough approximation')

    @st.cache_data(experimental_allow_widgets=True)
    def loadDatabase():
        #url= "https://docs.google.com/spreadsheets/d/1t8-3UUnGjH2Nv7vF2iHoj5NkEFeWftml9qhTTv3fE4A/edit?usp=sharing"
        # Create a connection object.
        conn = st.experimental_connection("gsheets", type=GSheetsConnection)
        phaseData = conn.read()       #if specific url is used (spreadsheet=url)
        return phaseData
    database=loadDatabase()
    allPhases= database.columns.values.tolist()

############################################## state variables ######################################################    
if 'diameter' not in st.session_state:
    st.session_state['diameter']=20
if 'voxelSize' not in st.session_state:
    st.session_state['voxelSize']=10
if 'filterThickness' not in st.session_state:
    st.session_state['filterThickness']=0.05
if 'DataSize' not in st.session_state:
    st.session_state['DataSize']=0.1
if 'maximumEnergy' not in st.session_state:
    st.session_state['maximumEnergy']=100
if 'minimumFeature' not in st.session_state:
    st.session_state['minimumFeature']=30
st.sidebar.title(':blue[Resolution]', help='_"Resolution is not a value but more like a state of mind"_ It depends not only on the voxel size but also on the quality of the final image. Tip: Aim for the highest quality possible, which can save time post-processing the 3D image and will increase the quality of your research')

########################################## Define voxel size vs diameter #################################################
##############thi 
def vs_diameter():
    ########### this is specific of a scanner configuration ### linear equation based on 1920px width (bin1)
    diameters=(12,40,150)                    # diameters 
    VS_1920Bin1=np.array([6,22,83])          # VS for the given diameters. All other correlations are calculated relative to this
    VS_2856Bin1=VS_1920Bin1*2/3
    VS_1920Bin2=VS_1920Bin1*2
    VS_2856Bin2=VS_1920Bin1*2/3*2
    VS_1920Bin3=VS_1920Bin1*3
    VS_2856Bin3=VS_1920Bin1*2/3*3          # this is the same as VS_1920Bin2, so only 5 lines are actually visible in the plot
    ############################# plots ################################
    RegressionData=pd.DataFrame({'Diameter':diameters,'VS_1920Bin1':VS_1920Bin1,'VS_2856Bin1':VS_2856Bin1,'VS_1920Bin2':VS_1920Bin2,'VS_2856Bin2':VS_2856Bin2,'VS_1920Bin3':VS_1920Bin3,'VS_2856Bin3':VS_2856Bin3})
    plotVS_Diam2856B1 = alt.Chart(RegressionData,height=400, width=600).mark_point().encode(x=alt.X('VS_2856Bin1:Q',title='Voxel Size (µm)'),y=alt.Y('Diameter:Q',title='Diameter (mm)')).transform_regression('VS_2856Bin1', 'Diameter').mark_line(color='#17becf',opacity=0.8)
    plotVS_Diam1920B1 = alt.Chart(RegressionData,height=400, width=600).mark_point().encode(x=alt.X('VS_1920Bin1:Q',title='Voxel Size (µm)'),y=alt.Y('Diameter:Q',title='Diameter (mm)')).transform_regression('VS_1920Bin1', 'Diameter').mark_line(color='#1f77b4',opacity=0.8)
    plotVS_Diam2856B2 = alt.Chart(RegressionData,height=400,width=600).mark_point().encode(x=alt.X('VS_2856Bin2:Q',title='Voxel Size (µm)'),y=alt.Y('Diameter:Q',title='Diameter (mm)')).transform_regression('VS_2856Bin2', 'Diameter').mark_line(color='#ff7f0e',opacity=0.8)
    plotVS_Diam1920B2 = alt.Chart(RegressionData,height=400,width=600).mark_point().encode(x=alt.X('VS_1920Bin2:Q',title='Voxel Size (µm)'),y=alt.Y('Diameter:Q',title='Diameter (mm)')).transform_regression('VS_1920Bin2', 'Diameter').mark_line(color='#ffbb78',opacity=0.8)
    plotVS_Diam2856B3 = alt.Chart(RegressionData,height=400,width=600).mark_point().encode(x=alt.X('VS_2856Bin3:Q',title='Voxel Size (µm)'),y=alt.Y('Diameter:Q',title='Diameter (mm)')).transform_regression('VS_2856Bin3', 'Diameter').mark_line(color='#2ca02c',opacity=0.8)
    plotVS_Diam1920B3 = alt.Chart(RegressionData,height=400,width=600).mark_point().encode(x=alt.X('VS_1920Bin3:Q',title='Voxel Size (µm)'),y=alt.Y('Diameter:Q',title='Diameter (mm)')).transform_regression('VS_1920Bin3', 'Diameter').mark_line(color='#98df8a',opacity=0.8)
    plot=plotVS_Diam2856B1 + plotVS_Diam1920B1 +plotVS_Diam2856B2 + plotVS_Diam1920B2 + plotVS_Diam2856B3 + plotVS_Diam1920B3
    if radio3=='1x' and radio4=='1920':
       st.session_state['voxelSize']=int(0.5627*st.session_state['diameter']-0.5293)             #linear correlations ######## in the future the coeficients could be calculated automatically using scipy
       markPoint=pd.DataFrame({'VS':[st.session_state['voxelSize']],'Diam':[st.session_state['diameter']]})   # Red Dot in the plot, coordinates along respective line
       st.session_state['DataSize']=11
    if radio3=='1x' and radio4=='2856':
       st.session_state['voxelSize']=int(0.3626*st.session_state['diameter']+0.0151)
       markPoint=pd.DataFrame({'VS':[st.session_state['voxelSize']],'Diam':[st.session_state['diameter']]})
       st.session_state['DataSize']=32
    if radio3=='2x' and radio4=='1920':
       st.session_state['voxelSize']=int(1.1254*st.session_state['diameter'] -1.0585)       
       markPoint=pd.DataFrame({'VS':[st.session_state['voxelSize']],'Diam':[st.session_state['diameter']]})
       st.session_state['DataSize']=1.4
    if radio3=='2x' and radio4=='2856':
       st.session_state['voxelSize']=int(0.7236*st.session_state['diameter']+0.4404)       
       markPoint=pd.DataFrame({'VS':[st.session_state['voxelSize']],'Diam':[st.session_state['diameter']]})
       st.session_state['DataSize']=4.3
    if radio3=='3x' and radio4=='1920':
       st.session_state['voxelSize']=int(1.6881*st.session_state['diameter']-1.5878)
       markPoint=pd.DataFrame({'VS':[st.session_state['voxelSize']],'Diam':[st.session_state['diameter']]})
       st.session_state['DataSize']=0.4
    if radio3=='3x' and radio4=='2856':
        st.session_state['voxelSize']=int(1.1254*st.session_state['diameter']-1.0585)        
        markPoint=pd.DataFrame({'VS':[st.session_state['voxelSize']],'Diam':[st.session_state['diameter']]})
        st.session_state['DataSize']=1.2
    plotMark = alt.Chart(markPoint,height=400,width=600).mark_point(color='red',size=120,fill='red').encode(x=alt.X('VS:Q',title='Voxel Size (µm)'),y=alt.Y('Diam:Q',title='Diameter (mm)'))
    plotAndMark=plot+plotMark
    st.altair_chart(plotAndMark,use_container_width=False)  
     
def attenuation_energy():
    ############## Plot Attenuation in the Composition Tab ###############################
    plot1= alt.Chart(database,width='container',height=400
                     ).mark_line(color='lightblue').encode(x=alt.X('Energy (kV):Q').scale(domain=(10,180)),
                                                           y=alt.Y(menuPhase1,title='Attenuation Coefficient (cm-1)').scale(type="log")).interactive()
    plot2= alt.Chart(database,width='container',height=400
                     ).mark_line(color='green').encode(x=alt.X('Energy (kV):Q').scale(domain=(10,180)),
                                                           y=alt.Y(menuPhase2,title='Attenuation Coefficient (cm-1)').scale(type="log")).interactive()
    plot3= alt.Chart(database,width='container',height=400
                     ).mark_line(color='orange').encode(x=alt.X('Energy (kV):Q').scale(domain=(10,180)),
                                                           y=alt.Y(menuPhase3,title='Attenuation Coefficient (cm-1)').scale(type="log")).interactive()
    plot4= alt.Chart(database,width='container',height=400
                     ).mark_line(color='red').encode(x=alt.X('Energy (kV):Q').scale(domain=(10,180)),
                                                           y=alt.Y(menuPhase4,title='Attenuation Coefficient (cm-1)').scale(type="log")).interactive()  
    plot=plot1 + plot2 + plot3 + plot4      
    st.altair_chart(plot,use_container_width=True)
def transmission():
    ########### Lambert-Beer law applied to the seleted phases, volume fractions and sample diameter
    attPhase1= database[menuPhase1]
    transm1=np.exp(-attPhase1*inFracPhase1*slideDiameter/10)
    attPhase2= database[menuPhase2]
    transm2=np.exp(-attPhase2*inFracPhase2*slideDiameter/10)
    attPhase3= database[menuPhase3]
    transm3=np.exp(-attPhase3*inFracPhase3*slideDiameter/10)
    attPhase4= database[menuPhase4]
    transm4=np.exp(-attPhase4*inFracPhase4*slideDiameter/10)
    totalTransm=transm1*transm2*transm3*transm4*100
    energy= database['Energy (kV)']
    ########################### Automatically calculates the filter #############################################
    attFilter= database['Fe']
    newAttFilt=[]
    newTotalTransm=[]
    newEnergy=[]
    i=0
    for t in totalTransm:
        tempEi=energy[i]      
        if t>0.001 and tempEi<310 and i<5:           # uses a narrow range of values, excludes transmissions close to 0 and high energies where the transmission is constant with the energy. 
            newTotalTransm.append(t)
            newEnergy.append(energy[i])
            newAttFilt.append(attFilter[i])
        if i>=5 and tempEi<310:                      # guarantees at least 5 datapoints to prevent error of the curve fit
            newTotalTransm.append(t)
            newEnergy.append(energy[i])
            newAttFilt.append(attFilter[i])
        i=i+1
    def EnVSTransm_function(x, a, b,c,d,e,f,g):
        return (a+b*x+c*x*x+d*x*x*x+g*x*x*x*x)/(e*x+f*x*x+1)
    params, covariance = curve_fit(EnVSTransm_function, newTotalTransm, newEnergy)
    a, b,c,d,e,f,g= params
    energyAt10percTransm=EnVSTransm_function(10,a, b,c,d,e,f,g)         # Calculates the energy at the point where the transmission through the sample is 10 percent (ideal case)
    energyAt1percTransm=EnVSTransm_function(1,a, b,c,d,e,f,g)           # Calculates the energy at the point where the transmission through the sample is 1 percent (fast case)
    def AttVSEn_function(x, a, b,c,d,e,f,g):
        return b+f*x+g*x*x/(b+c*x+a*x*x+d*x*x*x+e*x*x*x*x*x)
    params, covariance = curve_fit(AttVSEn_function, newEnergy, newAttFilt)
    a,b,c,d,e,f,g= params
    attCoefFiltAt10percTransm=AttVSEn_function(energyAt10percTransm,a,b,c,d,e,f,g)      # Calculates the attenuation coef. at energy with 10 % transmission (ideal case)
    attCoefFiltAt1percTransm=AttVSEn_function(energyAt1percTransm,a,b,c,d,e,f,g)        # Calculates the attenuation coef. at energy with 1 % transmission (fast case)
    ################ calculates the filter thickness for the selected option #####################
    if radioFilter=='Ideal':
        st.session_state['filterThickness']=-(np.log(0.2)*10)/attCoefFiltAt10percTransm
        if st.session_state['filterThickness']>3:
           st.session_state['filterThickness']=3
        st.write('Reference Filter Thickness (mm of Fe)', round(st.session_state['filterThickness'],1))
    if radioFilter=='No Filter':
        st.session_state['filterThickness']=0
        st.write('Reference Filter Thickness (mm of Fe)',round(st.session_state['filterThickness'],1))
    if radioFilter=='Fast':
        st.session_state['filterThickness']=-(np.log(0.5)*10)/attCoefFiltAt1percTransm  
        st.write('Reference Filter Thickness (mm of Fe)',round(st.session_state['filterThickness'],1))
    transmFilter=np.exp(-attFilter*st.session_state['filterThickness']/10)*100
    totalTransmFilter=totalTransm*transmFilter/100
    ###################### Plot total transmission ########################################
    TotalTransm4Plot={'Energy (kV)':energy,'Sample':totalTransm,'Filter':transmFilter, 'Filter+Sample':totalTransmFilter}
    dfTotalTransm4Plot=pd.DataFrame(TotalTransm4Plot)
    plotSample= alt.Chart(dfTotalTransm4Plot,width='container',height=400
                    ).mark_line(color='green').encode(x=alt.X('Energy (kV):Q').scale(domain=(20,180)),
                                                            y=alt.Y('Sample',title='Total Transmission (%)').scale(domain=(0,100))).interactive()
    plotSample_Filter=alt.Chart(dfTotalTransm4Plot,width='container',height=400
                    ).mark_line(color='orange').encode(x=alt.X('Energy (kV):Q').scale(domain=(20,180)),
                                                            y=alt.Y('Filter+Sample',title='Total Transmission (%)').scale(domain=(0,100))).interactive()
    plotFilter=alt.Chart(dfTotalTransm4Plot,width='container',height=400
                ).mark_line(color='lightblue').encode(x=alt.X('Energy (kV):Q').scale(domain=(20,180)),
                                                        y=alt.Y('Filter',title='Total Transmission (%)').scale(domain=(0,100))).interactive()
    plot=plotSample+plotSample_Filter+plotFilter
    st.altair_chart(plot,use_container_width=True)
    return dfTotalTransm4Plot, energyAt10percTransm

##################### Calculates the minimum feature of interest for the sidebar ############################
def updateMinFeature():
    if radio1=='Qualitative':
        st.session_state['minimumFeature']=st.session_state['voxelSize']*3
    if radio1=='Quantify':
        st.session_state['minimumFeature']=st.session_state['voxelSize']*5
    if radio1=='Classify':
       st.session_state['minimumFeature']=st.session_state['voxelSize']*7

############################ Controls the display in the tab geometry ################################
with tabGeometry:
    colDiam, colPurpose, colBin,colCam = st.columns(4, gap='large')
    with colDiam:
        st.subheader('Sample Diameter (mm)')
        slideDiameter= st.slider(' ', value=20, max_value=150, step=1,help='Larger diameters worsen the resolution. If the sample is irregular input the largest cross-section')
        st.session_state['diameter']=slideDiameter
    with colPurpose:
        st.subheader('Purpose of Study')
        radio1=st.radio(label='   ',options=['Qualitative','Quantify','Classify'], help='What kind of information do you need to answer your scientific question?')
    with colBin:
        st.subheader('Binning')
        radio3=st.radio(label=' ',options=['1x','2x','3x'], help='2x is recommended. Higher binning decreases the scanning time, image artefacts and data size, but worsens voxel size',index=1)
    with colCam:
        st.subheader('Detector width (px)')
        radio4=st.radio(label=' ',options=['2856','1920'],index=1,help='"1920" recommended if very dense phases are present and if the purpose is "Quantify" or "Classify". Smaller detectors decrease cone beam artifacts. Note that other values are possible, the two options are just a guide')
    st.divider()
    st.text('   ') #just some space
    vs_diameter()
    updateMinFeature()
    st.write(':grey[Each line represents a detector setting. The red dot highlights the selected setting]')

################################# Displays sidebar ###########################################
st.sidebar.metric(':blue[Voxel Size (um)]', st.session_state['voxelSize'], 
                  help='Calculated from the selected "Sample Diameter", "Binning" and "Detector width" in the :blue["Geometric Parameters"] tab')
st.sidebar.metric(':blue[Sample diameter (mm)]',st.session_state['diameter'],
                  help='Change with the slider in the :blue["Geometric Parameters"] tab. See the relation Diameter vs Voxel Size in the plot')
st.sidebar.metric(':blue[Minimum Feature Size (um)]', st.session_state['minimumFeature'],
                  help='The size of the smallest feature that you aim to study. It depends on the voxel size and the purpose of the study')
st.sidebar.metric(':blue[Data Size (Gb)]',st.session_state['DataSize'],
                  help='Expected size of the reconstructed 3D image. Relative to binning 1x, binning 2x generates 8x and binning 3x generates 27x smaller images')

############################ Controls the display in the tab Composition ################################
with tabComposition:
    col1,col2,col3=st.columns(3,gap='large')
    with col1:
        st.subheader('Main phases', help='The phases of interest are the ones that must be distinguished to answer the scientific question. Tip: if the sample has a complex matrix group the phases into classes of similar attenuation')
        menuPhase1=st.selectbox(label=':blue[Phase1]',options=allPhases,index=1)
        menuPhase2=st.selectbox(label=':green[Phase2]',options=allPhases,index=2) 
        menuPhase3=st.selectbox(label=':orange[Phase3]',options=allPhases,index=1)
        menuPhase4=st.selectbox(label=':red[Phase4]',options=allPhases,index=1)    
    with col2:
        st.subheader('Volume fractions', 
                  help='If you are an x-ray crossing the sample, how much yould you need to cross of each phase (values 0-1 and the sum of all phases should be 1-porosity)')
        inFracPhase1= st.number_input('Phase1 Volume Fraction (0-1)', value=0.0, min_value=0.0, max_value=1.0, step=0.02)
        inFracPhase2= st.number_input('Phase2 Volume Fraction (0-1)', value=0.0, min_value=0.0, max_value=1.0, step=0.02)
        inFracPhase3= st.number_input('Phase3 Volume Fraction (0-1)', value=0.0, min_value=0.0, max_value=1.0, step=0.02)
        inFracPhase4= st.number_input('Phase4 Volume Fraction (0-1)', value=0.0, min_value=0.0, max_value=1.0, step=0.02)
        porosity= int((1-inFracPhase1-inFracPhase2-inFracPhase3-inFracPhase4)*100)    
        st.write('Porosity (%):',porosity) #help='1 minus the sum of the volume fractions. Air is assumed to have attenuation coefficient =0'
    with col3:
        st.subheader('X-ray energy', 
                  help='The x-ray energy spectra ranges from the energy for which the transmission is above approx. 5% (blue curve) and the input "maximum energy"')
        radioFilter=st.radio(label='Filter',options=['No Filter','Fast','Ideal'],index=2, help='The type of filter is decided based on the transmission through the sample - depends on the diameter and composition. Ideal, is recommended for quantitative studies. Fast, could be sufficient for qualitative studies')
        st.text('   ') #just some space
        testEmax=st.slider('Maximum Energy (kV)', value=160, min_value=0, max_value=180, step=5,help='Tip: aim at a 160 kV, only use lower if necessary for good contrast')
        st.session_state['maximumEnergy']=testEmax

    ############################ Display plots ################################
    st.divider()
    col5,col4=st.columns(2,gap='large')
    with col4:
        st.subheader('Total transmission',
                  help='Percent of x-rays that penetrate through the :blue[Filter (light blue)], the :green[Sample (green)] and the :orange[Sample + Filter (orange)] at various energies')
        dfTotalTransm4Plot2, energyAt10percTransm = transmission()
        st.write(':green[Sample]  -  :blue[Filter]  -  :orange[Sample+Filter]')
        with st.expander('Transmission Table'):
            st.table(dfTotalTransm4Plot2)    
    with col5:
        st.subheader('Attenuation',
                  help='Energies with large difference between curves give better contrast. Note: if the curves are matching the phases will have similar greyvalues in the final image)')
        attenuation_energy()
        st.write(':grey[Each line corresponds to a phase selected with the same color]')
        with st.expander('Database of attenuation coefficients'):
            st.table(database)

############################ Controls the sidebar ################################
st.sidebar.title('  ') #just some space
st.sidebar.title(':violet[Contrast]', 
                 help='Contrast is reflected in the grey-scale of the different phases in the final image. It can be estimated by the difference in the attenuation curves within the energies boundaries [minimum transmissible energy, Emax], see Attenuation plot in the tab :violet["Composition"]')
st.sidebar.metric(':violet[Maximum Energy (kV)]',st.session_state['maximumEnergy'],help='Input with the slider in the tab :violet["Composition Parameter"]. Tip: 1) If contrast is not a problem aim at high kV, 2) At Emax, the transmission should be at least 10percent ')

############################ Calculation of time using empirical equations ################################
if st.session_state['voxelSize']<15:      # this is specific of the CoreTom: the power (W) equals the voxel size except bellow 15um.
    power = 15
else:
    power = st.session_state['voxelSize']
if radio3=='1x' and radio4=='1920':
    cameraFactor=1 # this camera was used as reference
    resolutionFactor=1
    scanTime=round((1.38*st.session_state['filterThickness']-0.0198*st.session_state['maximumEnergy']-0.0328*power+6.048)*cameraFactor,1)
if radio3=='2x' and radio4=='1920':
    cameraFactor=1
    resolutionFactor=2
    scanTime=round((0.68*st.session_state['filterThickness']-0.0109*st.session_state['maximumEnergy']-0.0152*power+2.607)*cameraFactor,1)
if radio3=='3x' and radio4=='1920':
    cameraFactor=1
    resolutionFactor=3 
    scanTime=round((0.328*st.session_state['filterThickness']-0.0055*st.session_state['maximumEnergy']-0.0068*power+1.19)*cameraFactor,1)
if radio3=='1x' and radio4=='2856':
    cameraFactor=1.4875
    resolutionFactor=1
    scanTime=round((1.38*st.session_state['filterThickness']-0.0198*st.session_state['maximumEnergy']-0.0328*power+6.048)*cameraFactor,1)
if radio3=='2x' and radio4=='2856':
    cameraFactor=1.4875
    resolutionFactor=2
    scanTime=round((0.68*st.session_state['filterThickness']-0.0109*st.session_state['maximumEnergy']-0.0152*power+2.607)*cameraFactor,1)
if radio3=='3x' and radio4=='2856':
    cameraFactor=1.4875
    resolutionFactor=3
    scanTime=round((0.328*st.session_state['filterThickness']-0.0055*st.session_state['maximumEnergy']-0.0068*power+1.19)*cameraFactor,1)
if scanTime<0.1:
    scanTime=0.1
#Unused time equation with binning as input 
#scanTime=(0.61*st.session_state['filterThickness']-0.0109*st.session_state['maximumEnergy']-1.3*resolutionFactor-0.0148*st.session_state['voxelSize']+5.65)*cameraFactor   #Bin1+Bin2+Bin3

############### Sets a warning for low counts ###########################
if energyAt10percTransm>st.session_state['maximumEnergy']:
    st.sidebar.title(':red[WARNING:] Limited counts, reduce sample diameter')
st.sidebar.title(' ') #just some space
st.sidebar.title(':green[Time]',
                 help='Tip: longer scans usually mean higher quality, which means less image processing time. Restric the time only if it is a time-lapse experiment or the access to the scanner is limited')
inNumbScans= st.sidebar.number_input(':green[Number of scans]', value=1, min_value=1, max_value=100, step=1, 
                                     help='this should acount for 1) how many samples, 2) how many scans per sample, e.g if the sample height> 0.8 x diameter. :red[IMPORTANT: Only aim at as many samples as you can realistically analyse]. Rule of thumb: processing 1 scan takes at least 1 days for qualitative studies and 1 week for quantitative studies')
experimentTime=round((scanTime+0.2)*inNumbScans,1) # adds 0.2 hrs to account for warmup?

if radio3=='1x' and radio4=='2856' and scanTime>6.2:
    st.sidebar.metric(':red[Experiment Time (hrs)]',experimentTime) 
elif radio3=='2x' and radio4=='2856' and scanTime>3.2:
    st.sidebar.metric(':red[Experiment Time (hrs)]',experimentTime)
elif radio3=='3x' and radio4=='2856' and scanTime>2.2:
    st.sidebar.metric(':red[Experiment Time (hrs)]',experimentTime)
elif radio3=='1x' and radio4=='1920' and scanTime>4.2:
    st.sidebar.metric(':red[Experiment Time (hrs)]',experimentTime) 
elif radio3=='2x' and radio4=='1920' and scanTime>2.2:
    st.sidebar.metric(':red[Experiment Time (hrs)]',experimentTime)
elif radio3=='3x' and radio4=='1920' and scanTime>1.5:
    st.sidebar.metric(':red[Experiment Time (hrs)]',experimentTime)
else: 
    st.sidebar.metric(':green[Experiment Time (hrs)]',experimentTime,help='It includes 12 min for every scan (to warmup and setting up the scan). Other tricks can be used to speedup the scan, ask a CT expert') 

