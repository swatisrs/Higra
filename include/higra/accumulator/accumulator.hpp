/***************************************************************************
* Copyright ESIEE Paris (2018)                                             *
*                                                                          *
* Contributor(s) : Benjamin Perret                                         *
*                                                                          *
* Distributed under the terms of the CECILL-B License.                     *
*                                                                          *
* The full license is in the file LICENSE, distributed with this software. *
****************************************************************************/

#pragma once

#include <functional>
#include <limits>
#include <vector>

namespace hg {

#define HG_ACCUMULATORS (min)(max)(mean)(counter)(sum)(prod)(first)(last)

    enum class accumulators {
        first,
        last,
        mean,
        min,
        max,
        counter,
        sum,
        prod
    };

    namespace accumulator_detail {

        /**
        * Marginal processing accumulator
        * @tparam S the storage type
        * @tparam vectorial bool: is dimension of storage > 0 (different from scalar)
        */
        template<typename S, bool vectorial>
        struct acc_marginal_impl {
        };

        template<typename S>
        struct acc_marginal_impl<S, true> {

            static const bool is_vectorial = true;

            using self_type = acc_marginal_impl<S, is_vectorial>;
            using value_type = typename std::iterator_traits<S>::value_type;
            using reducer_type = std::function<value_type(value_type, value_type)>;


            acc_marginal_impl(const S &storage_begin, const S &storage_end, const reducer_type &reducer,
                              const value_type &init_value) :
                    m_init_value(init_value),
                    m_reducer(reducer),
                    m_storage_begin(storage_begin),
                    m_storage_end(storage_end) {
            }

            template<typename ...Args>
            void
            initialize(Args &&...) {
                std::fill(m_storage_begin, m_storage_end, m_init_value);
            }

            template<typename T, typename ...Args>
            void
            accumulate(T value_begin, Args &&...) {
                auto s = m_storage_begin;
                for (; s != m_storage_end; s++, value_begin++) {
                    *s = m_reducer(*value_begin, *s);
                }
            };

            template<typename ...Args>
            void finalize(Args &&...) const {}

            void
            set_storage(S &storage_begin, S &storage_end) {
                m_storage_begin = storage_begin;
                m_storage_end = storage_end;
            }

            template<typename T>
            void
            set_storage(T &range) {
                m_storage_begin = range.begin();
                m_storage_end = range.end();
            }

        private:
            value_type m_init_value;
            reducer_type m_reducer;
            S m_storage_begin;
            S m_storage_end;
        };

        template<typename S>
        struct acc_marginal_impl<S, false> {

            static const bool is_vectorial = false;

            using self_type = acc_marginal_impl<S, is_vectorial>;
            using value_type = typename std::iterator_traits<S>::value_type;
            using reducer_type = std::function<value_type(value_type, value_type)>;

            acc_marginal_impl(const S &storage_begin, const S &, const reducer_type &reducer,
                              const value_type &init_value) :
                    m_init_value(init_value),
                    m_reducer(reducer),
                    m_storage_begin(storage_begin) {
            }

            template<typename ...Args>
            void
            initialize(Args &&...) {
                *m_storage_begin = m_init_value;
            }

            template<typename T, typename ...Args>
            void
            accumulate(const T value_begin, Args &&...) {
                *m_storage_begin = m_reducer(*value_begin, *m_storage_begin);
            };

            template<typename ...Args>
            void finalize(Args &&...) const {}

            void
            set_storage(S &storage_begin, S &) {
                m_storage_begin = storage_begin;
            }

            template<typename T>
            void
            set_storage(T &range) {
                m_storage_begin = range.begin();
            }

        private:
            value_type m_init_value;
            reducer_type m_reducer;
            S m_storage_begin;
        };


        /**
         * Mean accumulator
         * @tparam S the storage type
         * @tparam vectorial bool: is dimension of storage > 0 (different from scalar)
         */
        template<typename S, bool vectorial = true>
        struct acc_mean_impl {

            using self_type = acc_mean_impl<S, vectorial>;
            using value_type = typename std::iterator_traits<S>::value_type;
            static const bool is_vectorial = vectorial;

            acc_mean_impl(S storage_begin, S storage_end) :
                    m_counter(0),
                    m_storage_begin(storage_begin),
                    m_storage_end(storage_end) {
            }

            template<typename T = self_type, typename ...Args>
            typename std::enable_if_t<T::is_vectorial>
            initialize(Args &&...) {
                std::fill(m_storage_begin, m_storage_end, 0);
            }

            template<typename T = self_type, typename ...Args>
            typename std::enable_if_t<!T::is_vectorial>
            initialize(Args &&...) {
                *m_storage_begin = 0;
            }

            template<typename T1 = self_type, typename T, typename ...Args>
            std::enable_if_t<T1::is_vectorial>
            accumulate(T value_begin, Args &&...) {
                m_counter++;
                auto s = m_storage_begin;
                for (; s != m_storage_end; s++, value_begin++) {
                    *s += *value_begin;
                }
            }

            template<typename T1 = self_type, typename T, typename ...Args>
            std::enable_if_t<!T1::is_vectorial>
            accumulate(const T value_begin, Args &&...) {
                m_counter++;
                *m_storage_begin += *value_begin;
            }

            template<typename T = self_type, typename ...Args>
            typename std::enable_if_t<T::is_vectorial>
            finalize(Args &&...) const {
                for (auto s = m_storage_begin; s != m_storage_end; s++) {
                    *s /= m_counter;
                }
            }

            template<typename T = self_type, typename ...Args>
            typename std::enable_if_t<!T::is_vectorial>
            finalize(Args &&...) const {
                *m_storage_begin /= m_counter;
            }

            void set_storage(S storage_begin, S storage_end) {
                m_storage_begin = storage_begin;
                m_storage_end = storage_end;
            }

            template<typename T>
            void set_storage(T &range) {
                m_storage_begin = range.begin();
                m_storage_end = range.end();
            }

        private:
            std::size_t m_counter;
            S m_storage_begin;
            S m_storage_end;
        };

        /**
         * Counter accumulator
         * @tparam S the storage type
         * @tparam vectorial bool: is dimension of storage > 0 (different from scalar)
         */
        template<typename S, bool vectorial = true>
        struct acc_counter_impl {
            using value_type = typename std::iterator_traits<S>::value_type;
            using self_type = acc_counter_impl<S, vectorial>;
            static const bool is_vectorial = vectorial;

            acc_counter_impl(S storage_begin, S storage_end) :
                    m_storage_begin(storage_begin),
                    m_storage_end(storage_end) {
            }

            template<typename ...Args>
            void initialize(Args &&...) {
                *m_storage_begin = 0;
            }

            template<typename T, typename ...Args>
            void accumulate(const T &, Args &&...) {
                (*m_storage_begin)++;
            }

            template<typename ...Args>
            void finalize(Args &&...) const {}


            void set_storage(S storage_begin, S storage_end) {
                m_storage_begin = storage_begin;
                m_storage_end = storage_end;
            }

            template<typename T>
            void set_storage(T &range) {
                m_storage_begin = range.begin();
                m_storage_end = range.end();
            }

        private:
            S m_storage_begin;
            S m_storage_end;
        };

        /**
         * First accumulator
         * @tparam S the storage type
         * @tparam vectorial bool: is dimension of storage > 0 (different from scalar)
         */
        template<typename S, bool vectorial = true>
        struct acc_first_impl {
            using value_type = typename std::iterator_traits<S>::value_type;
            using self_type = acc_first_impl<S, vectorial>;
            static const bool is_vectorial = vectorial;

            acc_first_impl(S storage_begin, S storage_end) :
                    m_storage_begin(storage_begin),
                    m_storage_end(storage_end) {
            }

            template<typename ...Args>
            void initialize(Args &&...) {
                m_first = true;
            }

            template<typename T, typename ...Args>
            void accumulate(T value_begin, Args &&...) {
                if (m_first) {
                    m_first = false;
                    auto s = m_storage_begin;
                    for (; s != m_storage_end; s++, value_begin++) {
                        *s = *value_begin;
                    }
                }
            }

            template<typename ...Args>
            void finalize(Args &&...) const {}


            void set_storage(S storage_begin, S storage_end) {
                m_storage_begin = storage_begin;
                m_storage_end = storage_end;
            }

            template<typename T>
            void set_storage(T &range) {
                m_storage_begin = range.begin();
                m_storage_end = range.end();
            }

        private:
            bool m_first;
            S m_storage_begin;
            S m_storage_end;
        };

        /**
         * Last accumulator
         * @tparam S the storage type
         * @tparam vectorial bool: is dimension of storage > 0 (different from scalar)
         */
        template<typename S, bool vectorial = true>
        struct acc_last_impl {
            using value_type = typename std::iterator_traits<S>::value_type;
            using self_type = acc_last_impl<S, vectorial>;
            static const bool is_vectorial = vectorial;

            acc_last_impl(S storage_begin, S storage_end) :
                    m_storage_begin(storage_begin),
                    m_storage_end(storage_end) {
            }

            template<typename ...Args>
            void initialize(Args &&...) {

            }

            template<typename T1 = self_type, typename T, typename ...Args>
            std::enable_if_t<T1::is_vectorial>
            accumulate(T value_begin, Args &&...) {
                auto s = m_storage_begin;
                for (; s != m_storage_end; s++, value_begin++) {
                    *s = *value_begin;
                }
            }

            template<typename T1 = self_type, typename T, typename ...Args>
            std::enable_if_t<!T1::is_vectorial>
            accumulate(const T value_begin, Args &&...) {
                *m_storage_begin = *value_begin;
            }

            template<typename ...Args>
            void finalize(Args &&...) const {}


            void set_storage(S storage_begin, S storage_end) {
                m_storage_begin = storage_begin;
                m_storage_end = storage_end;
            }

            template<typename T>
            void set_storage(T &range) {
                m_storage_begin = range.begin();
                m_storage_end = range.end();
            }

        private:
            S m_storage_begin;
            S m_storage_end;
        };

    }

    struct accumulator_sum {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_marginal_impl<iterator_type, vectorial>(
                    storage.begin(),
                    storage.end(),
                    std::plus<value_type>(),
                    0);
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &input_shape) {
            return input_shape;
        }
    };

    struct accumulator_min {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_marginal_impl<iterator_type, vectorial>(
                    storage.begin(),
                    storage.end(),
                    [](value_type v1, value_type v2) { return std::min(v1, v2); },
                    std::numeric_limits<value_type>::max());
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &input_shape) {
            return input_shape;
        }
    };

    struct accumulator_max {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_marginal_impl<iterator_type, vectorial>(
                    storage.begin(),
                    storage.end(),
                    [](value_type v1, value_type v2) { return std::max(v1, v2); },
                    std::numeric_limits<value_type>::lowest());
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &input_shape) {
            return input_shape;
        }
    };

    struct accumulator_prod {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_marginal_impl<iterator_type, vectorial>(
                    storage.begin(),
                    storage.end(),
                    std::multiplies<value_type>(),
                    1);
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &input_shape) {
            return input_shape;
        }
    };

    struct accumulator_mean {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_mean_impl<iterator_type, vectorial>(storage.begin(), storage.end());
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &input_shape) {
            return input_shape;
        }
    };

    struct accumulator_counter {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_counter_impl<iterator_type, vectorial>(storage.begin(), storage.end());
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &) {
            return std::vector<std::size_t>();
        }
    };

    struct accumulator_first {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_first_impl<iterator_type, vectorial>(
                    storage.begin(),
                    storage.end());
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &input_shape) {
            return input_shape;
        }
    };

    struct accumulator_last {

        template<bool vectorial = true, typename S>
        auto make_accumulator(S &storage) const {
            using value_type = typename S::value_type;
            using iterator_type = decltype(storage.begin());
            return accumulator_detail::acc_last_impl<iterator_type, vectorial>(
                    storage.begin(),
                    storage.end());
        }

        template<typename shape_t>
        static
        auto get_output_shape(const shape_t &input_shape) {
            return input_shape;
        }
    };
}
