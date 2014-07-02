;*************************************************
; NCL Graphics: figure5.ncl
;************************************************
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl" 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl" 
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl" 
;************************************************
begin
;************************************************
; read in netCDF file

;  a = addfile("lnd/hist/b.e10.BG20TRCN.f09_g16.002.clm2.h0.1960-07.nc","r")     ; read in data
; same data from CAM
;  b = addfile("atm/hist/b.e10.BG20TRCN.f09_g16.002.cam2.h0.1960-07.nc","r")     ; read in data
;  PNG = "/lustre/atlas/scratch/ab3/cli062/higher-order/livv/plots/validation/"

  fsa = a->FSA(0,:,:)               ; grab the mean downwelling longwave rad
  fsa@lat = a->lat(:)
  fsa@lon = a->lon(:)
  fira = a->FIRA(0,:,:)               ; grab the mean net IR longwave rad, absorbed
  fira@lat = a->lat(:)
  fira@lon = a->lon(:)
  fsh = a->FSH(0,:,:)               ; grab the mean net IR longwave rad, absorbed
  fsh@lat = a->lat(:)
  fsh@lon = a->lon(:)
  fsh=-1*fsh
  qsoil = a->QSOIL(0,:,:)               ; grab the mean net IR longwave rad, absorbed
  qsoil=-1*2.835*1e6*qsoil
  qsoil@lat = a->lat(:)
  qsoil@lon = a->lon(:)

  rnet=fsa
  rnet@lat = a->lat(:)
  rnet@lon = a->lon(:)
  rnet=fsa-fira

;  is_mask = a->gris_mask(0,:,:)               ; grab the ice sheet mask
;  is_mask@lat = a->lat(:)
;  is_mask@lon = a->lon(:)

;  f = addfile("/lustre/atlas/scratch/4ue/cli062/CESM-CISM/Greenland_5km_v1.1_SacksRev_c110629.nc","r")
  e  = f->usrf(0,:,:)				; grab the elevation data
  e@lat2d = f->lat(0,:,:)
  e@lon2d = f->lon(0,:,:)


  printVarSummary(rnet)
  printMinMax(rnet,True)
  printVarSummary(fsh)
  printMinMax(fsh,True)
  printVarSummary(qsoil)
  printMinMax(qsoil,True)
;  printVarSummary(e)
;  printMinMax(e,True)

;************************************************
; create plot of elevation data, then an overlay of percent ice sheet/caps data
;************************************************
  wks = gsn_open_wks("png",PNG)                 ; open a ncgm file
  gsn_define_colormap(wks,"matlab_jet")         ; select color map
;  gsn_define_colormap(wks,"prcp_2")         ; select color map
  plot = new(3,graphic)

  res1 = True                                    ; plot mods desired
  res1@gsnDraw = False				; do not draw the plot
  res1@gsnFrame = False				; do not advance the frame
  res1@tiMainString  	     = "" 		 ; main title blank
  res1@gsnSpreadColors      = True               ; make cn span entire color map
  res1@mpFillOn             = False              ; turn off gray continents
  res1@cnLineLabelsOn        = False
  res1@mpProjection         =  "Aitoff"    ; map Projection
  res1@mpLimitMode         =  "LatLon"    ; how to zoom in
  res1@mpCenterLatF         =  70.
  res1@mpCenterLonF         =  -44.
  res1@mpMinLonF            = -55                ; set min lon
  res1@mpMaxLonF            = -30                ; set max lon
  res1@mpMinLatF            =  57.               ; set min lat
  res1@mpMaxLatF            =  85.               ; set min lat
  res1@mpOutlineOn          =  False             ; turn map outline off
  res1@cnLinesOn            = False 		; do not draw contour lines
  res1@cnFillOn             = True               ; color fill on
  res1@cnFillMode           = "RasterFill"       ; color fill on
  res1@cnLineLabelsOn       = False
  res1@lbOrientation       = "Vertical"		; make label bar vertical
  res1@pmLabelBarOrthogonalPosF = -0.01 		; move label bar closer
; contour levels for winter
  res1@cnLevelSelectionMode = "ExplicitLevels" ; use explicit levels
;  res1@cnLevels = ispan(190,340,10)             ; set the contour levels
  res1@cnLevels = (/-80,-55,-45,-35,-25,-15,-0,10,35,70,165/)            ; set the contour levels

  res2 = True                                    ; plot mods desired
  res2@gsnDraw = False				; do not draw the plot
  res2@gsnFrame = False				; do not advance the frame
  res2@tiMainString  	     = "" 		 ; main title blank
  res2@gsnSpreadColors      = True               ; make cn span entire color map
  res2@mpFillOn             = False              ; turn off gray continents
  res2@cnLineLabelsOn        = False
  res2@mpProjection         =  "Aitoff"    ; map Projection
  res2@mpLimitMode         =  "LatLon"    ; how to zoom in
  res2@mpCenterLatF         =  70.
  res2@mpCenterLonF         =  -44.
  res2@mpMinLonF            = -55                ; set min lon
  res2@mpMaxLonF            = -30                ; set max lon
  res2@mpMinLatF            =  57.               ; set min lat
  res2@mpMaxLatF            =  85.               ; set min lat
  res2@mpOutlineOn          =  False             ; turn map outline off
  res2@cnLinesOn            = False 		; do not draw contour lines
  res2@cnFillOn             = True               ; color fill on
  res2@cnFillMode           = "RasterFill"       ; color fill on
  res2@cnLineLabelsOn       = False
  res2@lbOrientation       = "Vertical"		; make label bar vertical
  res2@pmLabelBarOrthogonalPosF = -0.01 		; move label bar closer
; contour levels for summer
  res2@cnLevelSelectionMode = "ExplicitLevels" ; use explicit levels
;  res2@cnLevels = ispan(40,250,4)             ; set the contour levels
  res2@cnLevels = (/-160,-120,-80,-50,-30,-10,0,10,24,40,60/)            ; set the contour levels

  res3 = True                                    ; plot mods desired
  res3@gsnDraw = False				; do not draw the plot
  res3@gsnFrame = False				; do not advance the frame
  res3@tiMainString  	     = "" 		 ; main title blank
  res3@gsnSpreadColors      = True               ; make cn span entire color map
  res3@mpFillOn             = False              ; turn off gray continents
  res3@cnLineLabelsOn        = False
  res3@mpProjection         =  "Aitoff"    ; map Projection
  res3@mpLimitMode         =  "LatLon"    ; how to zoom in
  res3@mpCenterLatF         =  70.
  res3@mpCenterLonF         =  -44.
  res3@mpMinLonF            = -55                ; set min lon
  res3@mpMaxLonF            = -30                ; set max lon
  res3@mpMinLatF            =  57.               ; set min lat
  res3@mpMaxLatF            =  85.               ; set min lat
  res3@mpOutlineOn          =  False             ; turn map outline off
  res3@cnLinesOn            = False 		; do not draw contour lines
  res3@cnFillOn             = True               ; color fill on
  res3@cnFillMode           = "RasterFill"       ; color fill on
  res3@cnLineLabelsOn       = False
  res3@lbOrientation       = "Vertical"		; make label bar vertical
  res3@pmLabelBarOrthogonalPosF = -0.01 		; move label bar closer
; contour levels for summer
  res3@cnLevelSelectionMode = "ExplicitLevels" ; use explicit levels
;  res3@cnLevels = ispan(40,250,4)             ; set the contour levels
  res3@cnLevels = (/-125,-80,-50,-25,-10,-5,0,2,5/)            ; set the contour levels

  sres = True                                    ; plot mods desired
  sres = True                                    ; plot mods desired
  sres@cnFillOn             = False               ; color fill on
  sres@cnLinesOn            = True 		; do not draw contour lines
  sres@cnLineLabelsOn      = False 		; do not draw line labels
  sres@gsnDraw = False				; do not draw the plot
  sres@gsnFrame = False				; do not advance the frame

; contour levels for the elevation data
  sres@cnLevelSelectionMode = "ExplicitLevels"    ; use explicit levels
  sres@cnLevels = (/0,1000,2000,3000/)            ; set the contour levels

;  cres = True                                    ; plot mods desired
;  cres@cnFillOn             = False               ; color fill on
;  cres@cnLinesOn            = False 		; do not draw contour lines
;  cres@cnLineLabelsOn       = False
;  cres@cnLineThicknessF  = 4.                      ; line thickness
;  cres@cnLineDashPattern = 12                      ; dashed lines
;  cres@cnLineColor       = "Blue"                  ; blue contour lines
;  cres@cnLevelSelectionMode = "ExplicitLevels"    ; use explicit levels
;  cres@cnLevels = (/50,100/)            ; set the contour levels

  plotA = gsn_csm_contour_map_overlay(wks,rnet,e,res1,sres)   ; create plot
  plotB = gsn_csm_contour_map_overlay(wks,fsh,e,res2,sres)   ; create plot
  plotC = gsn_csm_contour_map_overlay(wks,qsoil,e,res2,sres)   ; create plot
  plot(0) = plotA
  plot(1) = plotB
  plot(2) = plotC

; for paneling
  resP = True
;  resP@gsnMaximize = True 
  gsn_panel(wks,plot,(/1,3/),resP)

  end

   
  