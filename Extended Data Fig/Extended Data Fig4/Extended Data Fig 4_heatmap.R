data4_sorted <- read.csv("data4_sorted.csv",row.names = 1)
library(pheatmap) 
library(RColorBrewer)
library(tibble)
library(ggplot2)

annotation_row2 <- read.csv("annotation_row2.csv",row.names = 1)
annotation_row2$type <- gsub("Gaba", "GABA", annotation_row2$type)
annotation_row2$type <- gsub("Dopa-GABA", "GABA-Dopa-", annotation_row2$type)
annotation_row2$type <- gsub("Hist-GABA", "GABA-Hist", annotation_row2$type)

annotation_row2$type <- sub("([a-zA-Z]+_)([0-9])$", "\\10\\2", annotation_row2$type)
anno_label <- read.csv("filtered_df2.csv",row.names = 1)
# 生成颜色向量

# 按行名合并数据框
merged_df <- merge(annotation_row2,anno_label,by = "row.names", all = TRUE)

# 重命名合并后的行名列
names(merged_df)[1] <- "row.names"
row.names(merged_df) <- merged_df$row.names
merged_df <- merged_df[ , -1]
merged_df <- merged_df[ , -3]

merged_df <- merged_df[order(merged_df$Freq),]
merged_df$Freq <- as.character(merged_df$Freq)

get_category <- function(x) {
  if (grepl("Dopa-GABA", x)) {
    return("Dopa-GABA")
  } else if (grepl("Dopa_", x)) {
    return("Dopa")
  } else if (grepl("GABA-Chol", x)) {
    return("GABA-Chol")
  } else if (grepl("GABA-Glut", x)) {
    return("GABA-Glut")
  } else if (grepl("GABA_", x)) {
    return("GABA")
  } else if (grepl("Glut_", x)) {
    return("Glut")
  } else if (grepl("GABA-Hist", x)) {
    return("GABA-Hist")
  } else {
    return("Other")
  }
}

strings = sort(unique(annotation_row2$type))
categories <- sapply(strings, get_category)


# 获取唯一类别
unique_categories <- unique(categories)

# 初始化颜色向量
string_colors <- character(length(strings))

# 为每个主要类别分配不同的调色板
palette_names <- c("Oranges", "Blues", "Purples", "YlGnBu","Greys","Reds","Greens" )
palette_index <- 1

for (category in unique_categories) {
  # 获取该类别的子集
  subset_indices <- which(categories == category)
  subset_strings <- strings[subset_indices]
  
  reds_palette <- colorRampPalette(brewer.pal(9, palette_names[palette_index]))
  # 创建颜色渐变函数
  
  palette_all <- reds_palette(length(subset_strings)+1)
  
  # 去掉第一个颜色
  palette <- palette_all[-1]
  
  # 创建调色板（循环使用不同的调色板）
  # palette <- brewer.pal(length(subset_strings), palette_names[palette_index])
  
  # 分配颜色
  string_colors[subset_indices] <- palette
  
  # 更新调色板索引
  palette_index <- palette_index %% length(palette_names) + 1
}


# 将颜色向量命名
names(string_colors) <- strings



# 创建颜色列表
ann_colors <- list(
  type = string_colors,
                   Freq = c("0" = "#e5eff9", "1" = "#56add8","2" = "#1f77a5", "3" = "#19455e"))
custom_colors <- colorRampPalette(c("blue", "white", "red"))(50)

heatmap = pheatmap(data4_sorted,
                   annotation_row=merged_df,
                   annotation_colors =ann_colors,
                   color = custom_colors,
                   show_rownames =F ,cluster_rows =F,cluster_cols=F)#,scale="row"
ggsave("heatmap.pdf", heatmap, width = 8, height = 8, dpi = 300)
