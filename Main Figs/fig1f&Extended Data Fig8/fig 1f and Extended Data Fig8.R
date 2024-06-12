suppressPackageStartupMessages(library(ComplexHeatmap))
library(cluster)
suppressPackageStartupMessages(library(dendextend))
suppressPackageStartupMessages(library(circlize))


# col_fun = colorRamp2(c(0,2000), c("white","red")) # for fig1 f

col_fun = colorRamp2(c(0,60), c("white","red")) # for Extended Data Fig 5
# col_fun = colorRamp2(c(0,1000, 2000), c( "white","yellow", "red"))
col_fun(seq(-2, 2))

#for fig1 f
# dfdata = read.table("all_neurons_fig1_final_new_sort.csv",row.names = "X",header = TRUE,sep = ",")

#for figs 5
dfdata = read.table("all_neurons_terminal_Extended Data Fig 8_sort.csv",row.names = "X",header = TRUE,sep = ",")

dfcol = read.table("all_neurons_plots_sort_area.csv",row.names = "X",header = TRUE,sep = ",")
dflabel = read.table("labels_all.csv",row.names = "X",header = TRUE,sep = ",")

dfdist = read.table("distance_mean_pct.csv",row.names = "X",header = TRUE,sep = ",")
d = as.dist(dfdist)
dend_rows = as.dendrogram(hclust(d,"ward.D2"))

dflabel$geno <- as.factor(dflabel$geno)
dflabel$location <- as.factor(dflabel$location)

geno_colors <- c('Agrp'='#0555ff','Avp'='#ffff00','Crh'='#b4b400','Wt(orexin)'='#ff00ff','Oxt'='#00ff00','Pmch'='#a52a2a','Pomc'='#f9ce00',
                 'Vip'='#e599bf','Adcyap1'='#ff0000', 
                 'Nts'='#000080','Pdyn'='#93278f','Penk'='#107010','Sst'='#0000ff',
                 'Tac1'='#b4b4b4','Tac2'='#00ffff','Trh'='#b0e0e6')
  

location_colors <- c(
   'LHA' = 'red',
  'VMH' = 'green',
  'AHN' = 'blue',
  'PH' = 'cyan',
  'PVH' = 'magenta',
  'MBO' = 'yellow',
  'TU' = 'brown',
  'MPO' = 'maroon',
  'DMH' = 'gray',
  'ARH' = 'navy',
  'MPN' = 'gold',
  'PVHd' = 'skyblue',
  'ZI' = 'orange',
  'PMv' = 'pink',
  'LPO' = 'turquoise',
  'others' = 'powderblue'
)


ha = HeatmapAnnotation(
  geno = dflabel$geno,
  location = dflabel$location,
  col = list(geno = geno_colors,location = location_colors),
  annotation_legend_param = list(
    geno = list(
      title = "Geno",
      at = names(geno_colors),
      labels = names(geno_colors)
)
      
    ),
    location = list(
      title = "Location",
      at = names(location_colors),
      labels = names(location_colors)
      # colors = location_colors
    )
  )

 
pdf("Extended Data Fig8.pdf", width = 16, height = 8)
ht = Heatmap(t(dfdata),col = col_fun,cluster_columns = dend_rows,
             column_split = 31,show_column_names = FALSE,
             row_split = t(dfcol),row_gap = unit(0.8, "mm"),
             column_gap = unit(0.8, "mm"),border = TRUE,
             cluster_rows = FALSE,top_annotation = ha)
draw(ht)
dev.off()

