require(tidyverse)

df <- read.csv('./data/2020-05-09/mlc1_cubic_0/local.csv') %>% top_n(100)

df$frame.time
