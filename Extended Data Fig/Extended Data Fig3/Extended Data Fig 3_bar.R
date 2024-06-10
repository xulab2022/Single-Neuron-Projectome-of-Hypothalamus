library(ggplot2)
df <- read.csv("bar_plot_df.csv",row.names = 1)
df$celltype <- factor(df$celltype, levels = df$celltype[order(df$celltypenum, decreasing = TRUE)])

p <- ggplot(df,aes(x=celltype,y=celltypenum))+geom_bar(stat="identity")+
  theme_classic()+xlab("")+ylab("Number of clusters")
ggsave("bar.pdf", p, width = 8, height = 3, dpi = 300)