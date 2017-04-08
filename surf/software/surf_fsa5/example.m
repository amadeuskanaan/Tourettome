%% clearallcloseall 
% ------------------------
clear all
close all


%% load toolboxes and define paths 
% ------------------------
for pathtoolbox = 1
   
    % you need to change the P variable to your path
    % and these paths too relative to where your data are 
    addpath('/Users/boris/02_toolboxes/surfstat')
   
    P               = '/Users/boris/01_projects/Example_jonny/';
    RPATH           = [P '/Results_R1/'];
    mkdir(RPATH);

end 



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

    % load:  Destrieux atlas
    % -----------------
    [vertices, label, colortable] = ...
    fs_read_annotation(['lh.aparc.a2009s.annot']);
    aparcleft = label; 
    for i = 1:size(colortable.table,1)
        mycode = colortable.table(i,5); 
        aparcleft(find(aparcleft == mycode)) = i;
    end

    % get segmentation
    [vertices, label, colortable] = ...
    fs_read_annotation(['rh.aparc.a2009s.annot']);
    aparcright = label; 
    for i = 1:size(colortable.table,1)
        mycode = colortable.table(i,5); 
        aparcright(find(aparcright == mycode)) = i;
    end

    aparc = [aparcleft;aparcright+100]; 
    aparc = aparc'; 
    
    CURV = SurfStatReadData({['fsaverage_curv_lh.asc'],['fsaverage_curv_rh.asc']});
 
    f = figure; 
        BoSurfStatViewData(sign(CURV),SM,'');
        colormap([0.6 0.6 0.6; 0.8 0.8 0.8]);
        exportfigbo(f,[RPATH 'brain.png'],'png',10); 
    close(f) 
   
    [~, PALS_L, ~] = ...
    fs_read_annotation(['lh.PALS_B12_Lobes.annot']);
    [~, PALS_R, ~] = ...
    fs_read_annotation(['rh.PALS_B12_Lobes.annot']);
    
    PALS          = [PALS_L(1:10242)' (PALS_R(1:10242)+1)'];
    upPALS = unique(PALS); 
    for i = 1:length(upPALS)
        PALS(PALS == upPALS(i)) = i; 
    end
    PALS(PALS<3) = 0; 
     f = figure; 
        SurfStatViewData(PALS,SM,'');
        exportfigbo(f,[RPATH 'PALS.png'],'png',10); 
    close(f)
    LOBES = PALS; 
       
    myLobes.code = unique(LOBES(LOBES>4))
    myLobes.name = {'OLobeL','OLobeR','FLobeL','FLobeR','PLobeL','PLobeR',...
                    'LimLobeL','LimLobeR','TLobeL','TLobeR'}
end


%% read abide csv phenotypic info
% ------------------------
for readcsv = 1
    
    cd(P)
    fid = fopen('abide_maxolinpittusmnyu_okt_extraADOSnew.csv'); % final group
    C   = textscan(fid,'%s%f%f%s%f%f%s%d%s%d%d%d%d%d%d%d%d%f%f%f%f%d','Delimiter',',','headerLines',1,'CollectOutput',1);
    fclose(fid);
    
    % These are the variables of interest 
    % -- 
    SITE        = C{1};
    CODE2       = C{2}(:,2);
    AGE         = C{4}(:,1);
    IQ          = C{6};
    CODE        = C{7};
    GROUP       = C{3};
    
end




%% read the thickness data 
% ------------------------
for loadct = 1
   cd([P 'ct5_20'])
   CODE2    = CODE; 
   T20      = zeros(length(CODE),size(SW.coord,2));
   myleft   = strcat(CODE2,'_lh2fsaverage5_20.mgh');
   myright  = strcat(CODE2,'_rh2fsaverage5_20.mgh');
   T20L      = SurfStatReadData(myleft); 
   T20R      = SurfStatReadData(myright); 
   T20       = [T20L, T20R];
   
end  


%% generate the mask using heuristic approach 
% ------------------------
mask  = mean(T20,1) > 0.4;





%% clusp setting across all analyses
% ------------------------
clusp = 0.005;


%% Figure 1 analyses: compare cortical thickness 
% ------------------------
for Figure1 = 1
      
    
        % keep 3 vector
        keep    = find(SITE==1)
           
        % clip 
        T       = T20(keep,:); 
        Gk      = GROUP(keep); 
        Ak      = AGE(keep);
        Ik      = IQ(keep);
        Sk      = SITE(keep); 
       
        
        % make terms 
        GR     = term(Gk);
        GL     = term(Glk);
        AG     = term(Ak); 
        IQU    = term(Ik); 
        SI     = term(Sk); 
 
        
        % Group analysis: 
        % controlled for site, age, iq
        % ---
        M        = 1 + SI + AG + IQU + GR;
        slm      = SurfStatLinMod(T,M,SW);
        slm      = SurfStatT(slm,GR.CONTROL-GR.ASD); 
        f=figure, SurfStatViewData(slm.t,SW,'')
  
end 