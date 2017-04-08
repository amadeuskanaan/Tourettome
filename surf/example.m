%% clearallcloseall 
% ------------------------
clear all
close all


%% load toolboxes and define paths 
% ------------------------
for pathtoolbox = 1
   
    % you need to change the P variable to your path
    % and these paths too relative to where your data are 
    addpath('/host/yeatman/local_raid/kanaan/Software/surfstat_chicago')
    addpath('/host/yeatman/local_raid/kanaan/Software')
   
    P               = '/host/yeatman/local_raid/kanaan/workspace/Tourettome/';
    RPATH           = [P '/Results_R1/'];
    mkdir(RPATH);

end 

ice = textread('ice.m');

%% read fs average stuff (surfaces, parcellations, curvature)
% ------------------------
for readsurfdata = 1
    
    cd([P 'surf_fsa5'])
    SPHERE = SurfStatReadSurf({'lh.sphere','rh.sphere'});
    S = SurfStatReadSurf({'lh.inflated','rh.inflated'});
    SW = SurfStatReadSurf({'lh.white','rh.white'});
    SP = SurfStatReadSurf({'lh.pial','rh.pial'});
    SM.tri = SW.tri;
    SM.coord = (SW.coord + SP.coord)./2;
    
    SInf = SW;
    SInf.coord = 0.2 *SW.coord + 0.8* S.coord;

   
    CURV = SurfStatReadData({['fsaverage_curv_lh.asc'],['fsaverage_curv_rh.asc']});
 
    f = figure; 
        BoSurfStatViewData(sign(CURV),SM,'');
        colormap([0.6 0.6 0.6; 0.8 0.8 0.8]);
        exportfigbo(f,[RPATH 'fsaverage.png'],'png',10); 
    close(f) 
   
 
end


%% read Tourettome csv phenotypic info
% ------------------------
for readcsv = 1
    
    cd(P)
    fid = fopen('/host/yeatman/local_raid/kanaan/workspace/Tourettome/phenotypic/phenotypic_tourettome.csv'); % final group
    C   = textscan(fid,'%s%s%s%f%s','Delimiter',',','headerLines',1,'CollectOutput',1);
    fclose(fid);
    
    % These are the variables of interest 
    % -- %id,site,group,age,sex

    ID         = C{1}(:,1);
    SITE       = C{1}(:,2);
    GROUP      = C{1}(:,3);
    AGE        = C{2};
    SEX        = C{3};
    
end




%% Read the thickness data 
% ------------------------
for loadct = 1
    
   cd([P 'FS_CT'])
   T20      = zeros(length(ID),size(SW.coord,2));
   myleft   = strcat(ID,'_lh2fsaverage5_20.mgh');
   myright  = strcat(ID,'_rh2fsaverage5_20.mgh');
   keep = ones(length(ID),1); 
   for i = 1:length(ID)
       try
           left      = SurfStatReadData1(myleft{i}); 
           right      = SurfStatReadData1(myright{i}); 
           T20(i,:)       = [left, right];

       catch
           keep(i) = 0; 
           disp(ID{i}) 
       end
   end
end  

keep        = find(keep); 
IDk         = ID(keep);
SITEk       = SITE(keep); 
GROUPk      = GROUP(keep);  
AGEk        = AGE(keep); 
SEXk        = SEX(keep); 
T20k        = T20(keep,:); 


%% generate the mask using heuristic approach 
% ------------------------
mask  = mean(T20k,1) > 0.4;

%% clusp setting across all analyses
% ------------------------
clusp = 0.005; 


%% Figure 1 analyses: compare cortical thickness 
% ------------------------
for Figure1 = 1
      
        clusp = 0.005;

        % make terms needed for the modeling  
        G     = term(GROUPk);
        SI    = term(SITEk);
        A     = term(AGEk); 
        SE    = term(SEXk); 
 
        % Linea model 
        % controlled for site, group, age, sex
        
        M        = 1 + SI + G + A + SE;
        slm      = SurfStatLinMod(T20k,M,SW);
        slm      = SurfStatT(slm,G.controls-G.patients); 

        %%%%%%%%%% CONTROLS > PATIENTS
        f=figure, SurfStatViewData(slm.t,SM,'t-stat controls>patients')
        SurfStatColLim([-4 4]) 
        exportfigbo(f,[RPATH 'Tourettome_Tstat_Controls_Patients.png'],'png',10)
        
        % multiple comparison correction (controls > patients)
        [pval, peak, clus, clusid] = SurfStatP(slm, mask, clusp); 
        effect = slm.t; 
        effect(pval.C>0.025) = 0; 
        dlmwrite([RPATH, 'thickness_tstat_CP.csv'], slm.t);
        dlmwrite([RPATH 'thickness_tstat_CP_fwe.csv'], effect);
        f=figure, 
            SurfStatViewData(effect, SM, 'FWE T-values controls>patients') 
            SurfStatColLim([2 5])
            colormap([0.8 .8 .8; ice/255])
            exportfigbo(f,[RPATH 'Tourettome_Tstat_FWE_clust025_Controls_Patients.png'],'png',10)           

                
        %%%%%%%%%% write thickness values of significant clusters 
        k = sum(clus.P<0.025); 
        sigclus = zeros(size(T20k,1),k); 
        for i = 1:sum(k) 
           sigclus(:,i) = mean(T20k(:,clusid==i),2); 
        end
        datatosave  = [G.controls G.patients  SI.PARIS SI.HANNOVER_A SI.Leipzig  sigclus]
        clust_table = array2table(datatosave,  'VariableNames', {'controls','patients','paris', 'hannover_a', 'leipzig', 'clust1', 'clust2', 'clust3'})
        writetable(clust_table,[RPATH 'thickness_table.csv'],'WriteRowNames',true)
        
            

        %%%%%%%%%% PATIENTS > CONTROLS  
        slm.t = -slm.t;  
        f=figure, SurfStatViewData(slm.t,SM,'t-stat patients>controls')
        SurfStatColLim([-4 4]) 
        exportfigbo(f,[RPATH 'Tourettome_Tstat_Patients_Controls.png'],'png',10)
        
        % multiple comparison correction (patients > controls)
        [pval, peak, clus, clusid] = SurfStatP(slm, mask, clusp); 
        effect2 = slm.t; 
        effect2(pval.C>0.025) = 0; 
        dlmwrite([RPATH, 'thickness_tstat_PC.csv'], slm.t);
        dlmwrite([RPATH 'thickness_tstat_PC_fwe.csv'], effect);
        
        f=figure, 
            SurfStatViewData(effect2, SM, 'FWE t-values patients>controls') 
            SurfStatColLim([2 5])
            colormap([0.8 .8 .8; ice/255])
            exportfigbo(f,[RPATH 'Tourettome_Tstat_FWE_clust025_Patients_Controls.png'],'png',10)

end 

%for covariance_analysis = 1    
%        seed = LCaudate; 
%        Seed = term(seed); 
%        % Linea model 
%        % controlled for site, age, iq
%        % ---
%        M        = 1 + SI + G + Seed + G*Seed ;
%        slm      = SurfStatLinMod(T20k,M,SW); 
%        slm      = SurfStatT(slm,(G.controls.*seed)-(G.patients.*seed) ); 
%end 