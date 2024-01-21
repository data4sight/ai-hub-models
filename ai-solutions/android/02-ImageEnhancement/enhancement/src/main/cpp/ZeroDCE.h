// -*- mode: cpp -*-
// =============================================================================
// @@-COPYRIGHT-START-@@
//
// Copyright (c) 2023 of Qualcomm Innovation Center, Inc. All rights reserved.
// SPDX-License-Identifier: BSD-3-Clause
//
// @@-COPYRIGHT-END-@@
// =============================================================================
//
// Created by shivmahe on 9/5/2023.
//

#ifndef SUPERRESOLUTION_ZERODCE_H
#define SUPERRESOLUTION_ZERODCE_H

#include "Model.h"

class ZeroDCE : public Model {

public:
    void preprocess(std::vector<float32_t> &dest_buffer, cv::Mat &img, std::vector<int> dims);
    void postprocess(cv::Mat &outputimg);
    void msg();


};


#endif //SUPERRESOLUTION_ZERODCE_H
